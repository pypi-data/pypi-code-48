"""
Module exports the 'Provider' abstract base class as well as the 'Hash', 'Cursor' and 'Creds' types
"""
from abc import ABC, abstractmethod
import re
import os
import logging
import random
from typing import TYPE_CHECKING, Generator, Optional, List, Union, Tuple, Dict, BinaryIO

from cloudsync.types import OInfo, DIRECTORY, DirInfo, Any
from cloudsync.exceptions import CloudFileNotFoundError, CloudFileExistsError, CloudTokenError, CloudNamespaceError
from cloudsync.oauth import OAuthConfig, OAuthProviderInfo
if TYPE_CHECKING:  # pragma: no cover
    from .event import Event

log = logging.getLogger(__name__)


# user-defined types.  must be serializable via msgpack and comparable
# mypy doesn't support cyclic definitions yet...
Hash = Union[Dict[str, 'Hash'], Tuple['Hash', ...], str, int, bytes, float, None]          # type: ignore
Cursor = Union[Dict[str, 'Cursor'], Tuple['Cursor', ...], str, int, bytes, float, None]    # type: ignore
Creds = Dict[str, Union[str, int]]


class Provider(ABC):                    # pylint: disable=too-many-public-methods
    """
    File storage provider.

    Override this to implement a provider capable of using the sync engine.

    Implementors are responsible for normalizing behavior, errors thrown, any needed caching.

    Some helpers are provided in this base class for oauth and  path manipulation.
    """

    # pylint: disable=multiple-statements
    name: str = None                          ; """Provider name"""
    sep: str = '/'                            ; """Path delimiter"""
    alt_sep: str = '\\'                       ; """Alternate path delimiter"""
    oid_is_path: bool = False                 ; """Objects stored in cloud are only referenced by path"""
    case_sensitive: bool = True               ; """Provider is case sensitive"""
    win_paths: bool = False                   ; """C: drive letter stuff needed for paths"""
    default_sleep: float = 0.01               ; """Per event loop sleep time"""
    _namespace: str = None                    ; """current namespace, if needed """
    _namespace_id: str = None                 ; """current namespace id, if needed """
    _oauth_info: OAuthProviderInfo = None     ; """OAuth providers can set this as a class variable"""
    _oauth_config: OAuthConfig = None         ; """OAuth providers can set this in init"""
    _listdir_page_size: Optional[int] = None  ; """Used for testing listdir"""

    # these are defined here for testing purposes only
    # providers setting these values will have them overridden and used for
    # multipart upload tests
    large_file_size: int = 0                  ; """Used for testing providers with separate large file handling"""
    upload_block_size: int = 0                ; """Used for testing providers with separate large file handling"""

    connection_id: Optional[str] = None       ; """Must remain constant between logins and must be unique to the login"""
    _creds: Optional[Any] = None              ; """Base class helpers to store creds"""
    __connected = False                       ; """Base class helper to fake a connection"""
    # pylint: enable=multiple-statements

    @abstractmethod
    def _api(self, *args, **kwargs):
        """Central function that wraps calls to the provider's api.

        Use this function on all calls that involve a network connection to the provider.

        Implmentations should catch provider specific errors and turn them into CloudException types.

        Suggestions for args can be:
               - endpoint + url params
               - a lambda with underlying provider calls

        Alternatively, _api can be written as a Guard with enter/exit code.
        """
        ...

    def get_quota(self) -> dict:    # pylint: disable=no-self-use
        """
        Returns a dict with of used (bytes), limit (bytes), optional login, and possibly other provider-specific info
        """
        return {"used": 0.0, "limit": 0.0, "login": None}

    def connect_impl(self, creds) -> str:  # pylint: disable=unused-argument
        """Connection implementation.

        Some providers don't need connections, so just don't implement/overload this method.

        Returns:
            Unique connection id that should be the same each time the same user connects.
            A combination of a provider name and a login/userid could be sufiicient, but
            it is suggested to use a provider specific identity, if available.
        """
        return self.connection_id or self.name

#    @final                             # uncomment when 3.8 is lowest supported
    def connect(self, creds):
        """Connect to provider.

        Generally providers should overload connect_impl, instead.
        """
        log.debug("connect %s (%s)", self.name, self.connection_id)
        self._creds = creds
        new_id = self.connect_impl(creds)
        if self.connection_id:
            if self.connection_id != new_id:
                self.disconnect()
                raise CloudTokenError("Cannot connect with mismatched credentials")
        else:
            self.connection_id = new_id
        self.__connected = True
        assert self.connected

    def set_creds(self, creds):
        """Set credentials without connecting."""
        self._creds = creds

    def reconnect(self):
        """Reconnect to provider, using existing creds.

        If a provider was previously connected, it should retain the creds used.
        This function should restore the connection if the creds are still valid

        Raises:
            CloudDisconnectedError on failure
        """
        connected = self.__connected
        if not connected:
            self.connect(self._creds)

    def disconnect(self):
        """Invalidates current connection, closes sockets, etc.
        """
        self.__connected = False

    @property
    def connected(self):
        """True if connected, false if not.

        If False, any use of the provider except the connect() function,
        must raise a CloudDisconnectedError
        """
        return self.connection_id is not None and self.__connected

    def authenticate(self) -> Creds:
        """Authenticate a connection.

        Returns:
            Creds: A JSON serializable object that can be used to log in.

        Raises:
                CloudTokenError on failure
        """
        if self._oauth_info:
            try:
                self._oauth_config.start_auth(self._oauth_info.auth_url, self._oauth_info.scopes)
                token = self._oauth_config.wait_auth(self._oauth_info.token_url)
            except Exception as e:
                log.error("oauth error %s", repr(e))
                self.disconnect()
                raise CloudTokenError(repr(e))

            return {"refresh_token": token.refresh_token,
                    "access_token": token.access_token}
        raise NotImplementedError()

    def interrupt_auth(self):
        """Iterrupt/stop a blocking authentication call."""
        if self._oauth_config:
            self._oauth_config.shutdown()
        else:
            raise NotImplementedError()

    @property
    @abstractmethod
    def latest_cursor(self) -> Cursor:
        """Get the latest cursor as of now."""
        ...

    @property
    @abstractmethod
    def current_cursor(self) -> Cursor:
        """Get the current cursor for the events generator"""
        ...

    @current_cursor.setter
    def current_cursor(self, val: Cursor) -> None:  # pylint: disable=no-self-use, unused-argument
        """Get the current cursor for the events generator"""
        ...

    @abstractmethod
    def events(self) -> Generator["Event", None, None]:
        """Yields events, possibly forever.

        If stopped, the event poller will sleep for self.default_sleep, and call this again.
        """
        ...

    @abstractmethod
    def walk(self, path, since=None) -> Generator["Event", None, None]:
        """List all files recursively, yielded as events"""
        ...

    @abstractmethod
    def upload(self, oid, file_like: BinaryIO, metadata=None) -> 'OInfo':
        """Upload a filelike to an existing object id, optionally setting metadata"""
        ...

    @abstractmethod
    def create(self, path, file_like: BinaryIO, metadata=None) -> 'OInfo':
        """Create a file at the specified path, setting contents and optionally setting metadata"""
        ...

    @abstractmethod
    def download(self, oid, file_like: BinaryIO):
        """Get the bytes of a specified object id"""
        ...

    @abstractmethod
    def rename(self, oid, path) -> str:
        """Rename an object to specified path"""
        # TODO: test that a renamed file can be renamed again
        # TODO: test that renaming a folder renames the children in the state file
        ...

    @abstractmethod
    def mkdir(self, path) -> str:
        """Create a folder"""
        ...

    @abstractmethod
    def delete(self, oid):
        """Delete an object"""
        ...
        ...

    @abstractmethod
    def exists_oid(self, oid) -> bool:
        """Returns true of object exists with specified oid"""
        return self.info_oid(oid) is not None

    @abstractmethod
    def exists_path(self, path) -> bool:
        """Returns true of object exists at the specified path"""
        return self.info_path(path) is not None

    @abstractmethod
    def listdir(self, oid) -> Generator[DirInfo, None, None]:
        """Yield one entry for each file at the directory pointed to by the specified object id"""
        ...

    # override this if your implementation is more efficient
    def hash_oid(self, oid) -> Hash:
        """Returns a provider specific hash associated with the object referred to"""
        info = self.info_oid(oid)
        return info.hash if info else None

    @abstractmethod
    def hash_data(self, file_like: BinaryIO) -> Hash:
        """Returns a provider specific hash from data"""
        ...

    @abstractmethod
    def info_path(self, path: str, use_cache=True) -> Optional[OInfo]:
        """Returns info for an object at a path, or None if not found"""
        ...

    @abstractmethod
    def info_oid(self, oid: str, use_cache=True) -> Optional[OInfo]:
        """Returns info for an object with specified oid, or None if not found"""
        ...

    def list_ns(self) -> List[str]:                        # pylint: disable=no-self-use
        """Yield one entry for each namespace supported, or None if namespaces are not needed"""
        return None

    @property
    def namespace(self) -> Optional[str]:
        return self._namespace

    @namespace.setter
    def namespace(self, ns: str):                          # pylint: disable=no-self-use
        raise CloudNamespaceError("This provider does not support namespaces")

    @property
    def namespace_id(self) -> Optional[str]:
        return self._namespace_id

    @namespace_id.setter
    def namespace_id(self, ns_id: str):                    # pylint: disable=no-self-use
        raise CloudNamespaceError("This provider does not support namespaces")

    @classmethod
    def uses_oauth(cls):
        return cls._oauth_info is not None

# CONVENIENCE
    def download_path(self, path, io):
        info = self.info_path(path)
        if not info or not info.oid:
            raise CloudFileNotFoundError()
        self.download(info.oid, io)

    def listdir_path(self, path):
        info = self.info_path(path)
        if not info:
            raise CloudFileNotFoundError()
        return self.listdir(info.oid)

    def rmtree(self, oid):
        try:
            for info in self.listdir(oid):
                if info.otype == DIRECTORY:
                    self.rmtree(info.oid)
                else:
                    self.delete(info.oid)
            self.delete(oid)
        except CloudFileNotFoundError:
            pass


# HELPER
    @classmethod
    def join(cls, *paths):
        """
        Joins a list of path strings in a provider-specific manner.

        Args:
            paths: zero or more paths
        """
        res = ""
        rl: List[str] = []
        for path in paths:
            if not path or path == cls.sep:
                continue

            if isinstance(path, str):
                rl = rl + [path.strip(cls.sep).strip(cls.alt_sep)]
                continue

            for sub_path in path:
                if sub_path is None or sub_path == cls.sep or sub_path == cls.alt_sep:
                    continue
                rl = rl + [sub_path.strip(cls.sep)]

        if not rl:
            return cls.sep

        res = cls.sep.join(rl)

        if not cls.win_paths or res[1] != ':':
            res = cls.sep + res

        return res

    def split(self, path):
        """Splits a path into a dirname, filename, just like 1os.path.split()1"""
        # todo cache regex
        index = path.rfind(self.sep)
        if self.alt_sep:
            index = max(index, path.rfind(self.alt_sep))

        if index == -1:
            return "", path
        if index == 0:
            return self.sep, path[index + 1:]
        return path[:index], path[index+1:]

    def normalize_path(self, path: str):
        """Used internally for comparing paths in a case and sep insensitive manner, as appropriate."""
        norm_path = path.rstrip(self.sep)
        if self.sep in ["\\", "/"]:
            parts = re.split(r'[\\/]+', norm_path)
        else:
            parts = re.split(r'[%s]+' % self.sep, norm_path)
        norm_path = self.join(*parts)
        if not self.case_sensitive:
            norm_path = norm_path.lower()
        return norm_path

    def is_subpath(self, folder, target, strict=False):
        """True if the target is within the folder.

        Args:
            folder: the directory
            target: the potential sub-file or folder
            strict: whether to return True if folder==target
        """
        sep = self.sep
        alt_sep = self.alt_sep
        if alt_sep:
            folder = folder.replace(alt_sep, sep)
            target = target.replace(alt_sep, sep)

        # Will return True for is-same-path in addition to target
        folder_full = str(folder)
        folder_full = folder_full.rstrip(sep)
        target_full = str(target)
        target_full = target_full.rstrip(sep)
        # .lower() instead of normcase because normcase will also mess with separators
        if not self.case_sensitive:
            folder_full_case = folder_full.lower()
            target_full_case = target_full.lower()
        else:
            folder_full_case = folder_full
            target_full_case = target_full

        # target is same as folder, or target is a subpath (ensuring separator is there for base)
        if folder_full_case == target_full_case:
            return False if strict else sep
        elif len(target_full) > len(folder_full) and target_full[len(folder_full)] == sep:
            if target_full_case.startswith(folder_full_case):
                return target_full[len(folder_full):]
            else:
                return False
        return False

    def replace_path(self, path, from_dir, to_dir):
        """Replaces from_dir with to_dir in path, but only if from_dir `is_subpath` of path."""
        relative = self.is_subpath(from_dir, path)
        if relative:
            retval = to_dir + (relative if relative != self.sep else "")
            return retval if relative != "" else self.sep
        raise ValueError("replace_path used without subpath")

    def paths_match(self, patha, pathb):
        """True if two paths are equal, uses normalize_path()."""
        if patha is None and pathb is None:
            return True
        elif patha is None or pathb is None:
            return False

        return self.normalize_path(patha) == self.normalize_path(pathb)

    def dirname(self, path: str):
        """Just like `os.dirname`, but for provider paths."""
        ret, _ = self.split(path)
        return ret

    def basename(self, path: str):
        """Just like `os.basename`, but for provider paths."""
        _, ret = self.split(path)
        return ret

    def _verify_parent_folder_exists(self, path):
        parent_path = self.dirname(path)
        if parent_path != self.sep:
            parent_obj = self.info_path(parent_path)
            if parent_obj is None:
                # perhaps this should separate "FileNotFound" and "non-folder parent exists"
                # and raise different exceptions
                raise CloudFileNotFoundError(parent_path)
            if parent_obj.otype != DIRECTORY:
                raise CloudFileExistsError(parent_path)

    def mkdirs(self, path):
        """Makes a directory and intervening directories, returns the oid of the leaf"""
        log.debug("mkdirs %s", path)
        try:
            oid = self.mkdir(path)
            # todo update state
        except CloudFileExistsError:
            # todo: mabye CloudFileExistsError needs to have an oid and/or path in it
            # at least optionally
            info = self.info_path(path)
            if info and info.otype == DIRECTORY:
                oid = info.oid
            else:
                raise
        except CloudFileNotFoundError:
            ppath, _ = self.split(path)
            if ppath == path:
                raise
            log.debug("mkdirs parent, %s", ppath)
            unused_oid = self.mkdirs(ppath)
            try:
                oid = self.mkdir(path)
                # todo update state
            except CloudFileNotFoundError:
                # when syncing, file exists seems to hit better conflict code for these sorts of situations
                # but this is a guess.  todo: scenarios that make this happen
                raise CloudFileExistsError("f'ed up mkdir")
        return oid

# TEST ################################################
    def test_short_poll_only(self, short_poll_only: bool):  # pylint: disable=unused-argument, no-self-use
        pass

    @classmethod
    def test_instance(cls):
        """Override to enable CI testing of your class, see oauth_test_instance code for an example

        Returns:
            Provider: an instance of an provider, with "creds" set to the creds blob
        """
        if cls._oauth_info is not None:
            # pull environment info based on class name prefix
            return cls.oauth_test_instance(prefix=cls.name.upper())             # pylint: disable=no-member
        else:
            # no connection needed
            cls._test_creds: Dict[str, str] = None            # type: ignore
            return cls()

    def _clear_cache(self, *, oid=None, path=None):  # pylint: disable=unused-argument, no-self-use
        # override this method if the provider implements a cache, to permit the internal cache to be cleared on demand
        # the _clear_cache method in the subclass should return True
        return False

    @classmethod
    def oauth_test_instance(cls, prefix: str, token_key="refresh_token", token_sep="|", port_range: Tuple[int, int] = None, host_name=None):
        """Helper function for oauth providers.

        Args:
            prefix: environment varible prefix
            token_key: creds dict key
            token_sep: multi-env var token separator
            port_range: if any, specify tuple
        """

        tokens = os.environ.get("%s_TOKEN" % prefix).split(token_sep)
        token = tokens[random.randrange(0, len(tokens))]

        if token.startswith("file:"):
            token = open(token[5:]).read()

        creds = {
            token_key: token,
        }
        cls._test_creds = creds                                          # type: ignore
        return cls(OAuthConfig(                                         # type: ignore
            app_id=os.environ.get("%s_APP_ID" % prefix),
            app_secret=os.environ.get("%s_APP_SECRET" % prefix),
            host_name=host_name,
            port_range=port_range))
