"""A memory file system implemented on top of winfspy.

Useful for testing and as a reference.
"""

import sys
import time
import logging
import argparse
import threading
from functools import wraps
from pathlib import PureWindowsPath

from winfspy import (
    FileSystem,
    BaseFileSystemOperations,
    enable_debug_log,
    FILE_ATTRIBUTE,
    CREATE_FILE_CREATE_OPTIONS,
    NTStatusObjectNameNotFound,
    NTStatusDirectoryNotEmpty,
    NTStatusNotADirectory,
    NTStatusObjectNameCollision,
    NTStatusAccessDenied,
    NTStatusEndOfFile,
)
from winfspy.plumbing.winstuff import filetime_now, SecurityDescriptor


def operation(fn):
    """Decorator for file system operations.

    Provides both logging and thread-safety
    """
    name = fn.__name__

    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        head = args[0] if args else None
        tail = args[1:] if args else ()
        try:
            with self._thread_lock:
                result = fn(self, *args, **kwargs)
        except Exception as exc:
            logging.info(f" NOK | {name:20} | {head!r:20} | {tail!r:20} | {exc!r}")
            raise
        else:
            logging.info(f" OK! | {name:20} | {head!r:20} | {tail!r:20} | {result!r}")
            return result

    return wrapper


class BaseFileObj:
    @property
    def name(self):
        return self.path.name

    def __init__(self, path, attributes):
        self.path = path
        self.attributes = attributes
        now = filetime_now()
        self.creation_time = now
        self.last_access_time = now
        self.last_write_time = now
        self.change_time = now
        self.index_number = 0

        self.security_descriptor = SecurityDescriptor(
            "O:BAG:BAD:P(A;;FA;;;SY)(A;;FA;;;BA)(A;;FA;;;WD)"
        )

    def get_file_info(self):
        return {
            "file_attributes": self.attributes,
            "allocation_size": self.allocation_size,
            "file_size": self.file_size,
            "creation_time": self.creation_time,
            "last_access_time": self.last_access_time,
            "last_write_time": self.last_write_time,
            "change_time": self.change_time,
            "index_number": self.index_number,
        }

    def __repr__(self):
        return f"{type(self).__name__}:{self.name}"


class FileObj(BaseFileObj):
    def __init__(self, path, attributes, data=b""):
        super().__init__(path, attributes)
        self.data = bytearray(data)
        self.attributes |= FILE_ATTRIBUTE.FILE_ATTRIBUTE_ARCHIVE
        assert not self.attributes & FILE_ATTRIBUTE.FILE_ATTRIBUTE_DIRECTORY

    @property
    def file_size(self):
        return len(self.data)

    @property
    def allocation_size(self):
        if len(self.data) % 4096 == 0:
            return len(self.data)
        else:
            return ((len(self.data) // 4096) + 1) * 4096


class FolderObj(BaseFileObj):
    def __init__(self, path, attributes):
        super().__init__(path, attributes)
        self.file_size = 0
        self.allocation_size = 0
        assert self.attributes & FILE_ATTRIBUTE.FILE_ATTRIBUTE_DIRECTORY


class OpenedObj:
    def __init__(self, file_obj):
        self.file_obj = file_obj

    def __repr__(self):
        return f"{type(self).__name__}:{self.file_obj.name}"


class InMemoryFileSystemOperations(BaseFileSystemOperations):
    def __init__(self, volume_label):
        super().__init__()
        if len(volume_label) > 31:
            raise ValueError("`volume_label` must be 31 characters long max")

        max_file_nodes = 1024
        max_file_size = 16 * 1024 * 1024
        file_nodes = 1

        self._volume_info = {
            "total_size": max_file_nodes * max_file_size,
            "free_size": (max_file_nodes - file_nodes) * max_file_size,
            "volume_label": volume_label,
        }

        self._root_path = PureWindowsPath("/")
        self._entries = {
            self._root_path: FolderObj(self._root_path, FILE_ATTRIBUTE.FILE_ATTRIBUTE_DIRECTORY),
        }
        self._thread_lock = threading.Lock()

    @operation
    def get_volume_info(self):
        return self._volume_info

    @operation
    def set_volume_label(self, volume_label):
        self._volume_info["volume_label"] = volume_label

    @operation
    def get_security_by_name(self, file_name):
        file_name = PureWindowsPath(file_name)

        # Retrieve file
        try:
            file_obj = self._entries[file_name]
        except KeyError:
            raise NTStatusObjectNameNotFound()

        return (
            file_obj.attributes,
            file_obj.security_descriptor.handle,
            file_obj.security_descriptor.size,
        )

    @operation
    def create(
        self,
        file_name,
        create_options,
        granted_access,
        file_attributes,
        security_descriptor,
        allocation_size,
    ):
        file_name = PureWindowsPath(file_name)

        # `granted_access` is already handle by winfsp
        # `allocation_size` useless for us
        # `security_descriptor` is not supported yet

        # Retrieve file
        try:
            parent_file_obj = self._entries[file_name.parent]
            if isinstance(parent_file_obj, FileObj):
                raise NTStatusNotADirectory()
        except KeyError:
            raise NTStatusObjectNameNotFound()

        # File/Folder already exists
        if file_name in self._entries:
            raise NTStatusObjectNameCollision()

        if create_options & CREATE_FILE_CREATE_OPTIONS.FILE_DIRECTORY_FILE:
            file_obj = self._entries[file_name] = FolderObj(file_name, file_attributes)
        else:
            file_obj = self._entries[file_name] = FileObj(file_name, file_attributes)

        return OpenedObj(file_obj)

    @operation
    def get_security(self, file_context):
        sd = file_context.file_obj.security_descriptor
        return sd.handle, sd.size

    @operation
    def set_security(self, file_context, security_information, modification_descriptor):
        # TODO
        pass

    @operation
    def rename(self, file_context, file_name, new_file_name, replace_if_exists):
        file_name = PureWindowsPath(file_name)
        new_file_name = PureWindowsPath(new_file_name)

        # Retrieve file
        try:
            file_obj = self._entries[file_name]

        except KeyError:
            raise NTStatusObjectNameNotFound()

        if new_file_name in self._entries:
            if not replace_if_exists:
                raise NTStatusObjectNameCollision()
            if not isinstance(file_obj, FileObj):
                raise NTStatusAccessDenied()

        for entry_path in list(self._entries):
            try:
                relative = entry_path.relative_to(file_name)
                new_entry_path = new_file_name / relative
                entry = self._entries.pop(entry_path)
                entry.path = new_entry_path
                self._entries[new_entry_path] = entry
            except ValueError:
                continue

    @operation
    def open(self, file_name, create_options, granted_access):
        file_name = PureWindowsPath(file_name)

        # `granted_access` is already handle by winfsp

        # Retrieve file
        try:
            file_obj = self._entries[file_name]
        except KeyError:
            raise NTStatusObjectNameNotFound()

        return OpenedObj(file_obj)

    @operation
    def close(self, file_context):
        pass

    @operation
    def get_file_info(self, file_context):
        return file_context.file_obj.get_file_info()

    @operation
    def set_basic_info(
        self,
        file_context,
        file_attributes,
        creation_time,
        last_access_time,
        last_write_time,
        change_time,
        file_info,
    ) -> dict:

        file_obj = file_context.file_obj
        if file_attributes != FILE_ATTRIBUTE.INVALID_FILE_ATTRIBUTES:
            file_obj.attributes = file_attributes
        if creation_time:
            file_obj.creation_time = creation_time
        if last_access_time:
            file_obj.last_access_time = last_access_time
        if last_write_time:
            file_obj.last_write_time = last_write_time
        if change_time:
            file_obj.change_time = change_time

        return file_obj.get_file_info()

    @operation
    def set_file_size(self, file_context, new_size, set_allocation_size):
        file_obj = file_context.file_obj
        if set_allocation_size:
            if new_size < file_obj.file_size:
                file_obj.data = file_obj.data[:new_size]
        else:
            if new_size < file_obj.file_size:
                file_obj.data = file_obj.data[:new_size]
            if new_size > file_obj.file_size:
                file_obj.data = file_obj.data + bytearray(new_size - file_obj.file_size)

    @operation
    def can_delete(self, file_context, file_name: str) -> None:
        file_name = PureWindowsPath(file_name)

        # Retrieve file
        try:
            file_obj = self._entries[file_name]
        except KeyError:
            raise NTStatusObjectNameNotFound

        if isinstance(file_obj, FolderObj):
            for entry in self._entries.keys():
                try:
                    if entry.relative_to(file_name).parts:
                        raise NTStatusDirectoryNotEmpty()
                except ValueError:
                    continue

    @operation
    def read_directory(self, file_context, marker):
        entries = []
        file_obj = file_context.file_obj

        # Not a directory
        if isinstance(file_obj, FileObj):
            raise NTStatusNotADirectory()

        # The "." and ".." should ONLY be included if the queried directory is not root
        if file_obj.path != self._root_path:
            parent_obj = self._entries[file_obj.path.parent]
            entries.append({"file_name": ".", **file_obj.get_file_info()})
            entries.append({"file_name": "..", **parent_obj.get_file_info()})

        # Loop over all entries
        for entry_path, entry_obj in self._entries.items():
            try:
                relative = entry_path.relative_to(file_obj.path)
            # Filter out unrelated entries
            except ValueError:
                continue
            # Filter out ourself or our grandchildren
            if len(relative.parts) != 1:
                continue
            # Add direct chidren to the entry list
            entries.append({"file_name": entry_path.name, **entry_obj.get_file_info()})

        # Sort the entries
        entries = sorted(entries, key=lambda x: x["file_name"])

        # No filtering to apply
        if marker is None:
            return entries

        # Filter out all results before the marker
        for i, entry in enumerate(entries):
            if entry["file_name"] == marker:
                return entries[i + 1 :]

    @operation
    def get_dir_info_by_name(self, file_context, file_name):
        path = file_context.file_obj.path / file_name
        try:
            entry_obj = self._entries[path]
        except KeyError:
            raise NTStatusObjectNameNotFound()

        return {"file_name": file_name, **entry_obj.get_file_info()}

    @operation
    def read(self, file_context, offset, length):
        file_obj = file_context.file_obj

        if offset >= len(file_obj.data):
            raise NTStatusEndOfFile()

        return file_obj.data[offset : offset + length]

    @operation
    def write(self, file_context, buffer, offset, write_to_end_of_file, constrained_io):
        file_obj = file_context.file_obj
        length = len(buffer)

        if constrained_io:
            if offset >= len(file_obj.data):
                return 0
            end_offset = min(len(file_obj.data), offset + length)
            transferred_length = end_offset - offset
            file_obj.data[offset:end_offset] = buffer[:transferred_length]
            return transferred_length

        else:
            if write_to_end_of_file:
                offset = len(file_obj.data)
            end_offset = offset + length
            file_obj.data[offset:end_offset] = buffer
            return length

    @operation
    def cleanup(self, file_context, file_name, flags) -> None:
        # TODO: expose FspCleanupDelete&friends
        if flags & 1:
            file_name = PureWindowsPath(file_name)
            try:
                del self._entries[file_name]
            except KeyError:
                raise NTStatusObjectNameNotFound()

    @operation
    def overwrite(
        self, file_context, file_attributes, replace_file_attributes: bool, allocation_size: int
    ) -> None:
        file_obj = file_context.file_obj
        file_attributes |= FILE_ATTRIBUTE.FILE_ATTRIBUTE_ARCHIVE
        if replace_file_attributes:
            file_obj.attributes = file_attributes
        else:
            file_obj.attributes |= file_attributes
        if allocation_size < file_obj.file_size:
            file_obj.data = file_obj.data[:allocation_size]


def create_memory_file_system(
    mountpoint, label="memfs", verbose=True, debug=False,
):
    if debug:
        enable_debug_log()
    if verbose:
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    operations = InMemoryFileSystemOperations(label)
    fs = FileSystem(
        str(mountpoint),
        operations,
        sector_size=512,
        sectors_per_allocation_unit=1,
        volume_creation_time=filetime_now(),
        volume_serial_number=0,
        file_info_timeout=1000,
        case_sensitive_search=1,
        case_preserved_names=1,
        unicode_on_disk=1,
        persistent_acls=1,
        post_cleanup_when_modified_only=1,
        um_file_context_is_user_context2=1,
        file_system_name=str(mountpoint),
        prefix="",
        debug=debug,
        # security_timeout_valid=1,
        # security_timeout=10000,
    )
    return fs


def main(mountpoint, label, verbose, debug):
    fs = create_memory_file_system(mountpoint, label, verbose, debug)
    try:
        print("Starting FS")
        fs.start()
        print("FS started, keep it running forever")
        while True:
            time.sleep(1)

    finally:
        print("Stopping FS")
        fs.stop()
        print("FS stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("mountpoint")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-l", "--label", type=str, default="memfs")
    args = parser.parse_args()
    main(args.mountpoint, args.label, args.verbose, args.debug)
