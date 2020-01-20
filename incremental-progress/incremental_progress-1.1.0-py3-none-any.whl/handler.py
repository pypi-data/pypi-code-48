import shutil


class ProgressFileHandler:
    @classmethod
    def should_operate(cls, file_path, monitored_files, monitored_extensions):
        """
        Determines if the file is in the watched path
        and that the file extension is one that should be
        watched
        """
        file_extension = file_path.split(".")[-1]

        if file_path in monitored_files and file_extension in monitored_extensions:
            return True

        return False

    @classmethod
    def copy_source(cls, file_path, file_copy_path):
        """
        Copy the modified file to the STORAGE_PATH directory
        """
        file_extension = file_path.split(".")[-1]
        shutil.copy(file_path, f"{file_copy_path}.{file_extension}")
