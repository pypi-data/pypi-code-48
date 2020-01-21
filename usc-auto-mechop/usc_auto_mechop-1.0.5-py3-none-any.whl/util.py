import os
import re

import logging
logger = logging.getLogger(__name__)


class cd:
    """
    Context manager for changing the current working directory
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def match_filename_to_student(filename, section):
    try:
        usc_id_from_filename = int(re.search("\d{10}", filename).group(0))
        student = section[usc_id_from_filename]
        logger.debug('Matched file {} to student {}.'.format(filename, student.name))
        return student
    except KeyError:
        return None