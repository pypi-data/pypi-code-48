import os
import tempfile
import unittest

from avocado.core import exit_codes
from avocado.utils import process
from avocado.utils import script
from avocado.utils import path as utils_path

from .. import AVOCADO, BASEDIR, temp_dir_prefix


SCRIPT_CONTENT = """#!/bin/bash
touch %s
exec -- $@
"""

DUMMY_CONTENT = """#!/bin/bash
exec -- $@
"""


def missing_binary(binary):
    try:
        utils_path.find_command(binary)
        return False
    except utils_path.CmdNotFoundError:
        return True


class WrapperTest(unittest.TestCase):

    def setUp(self):
        prefix = temp_dir_prefix(__name__, self, 'setUp')
        self.tmpdir = tempfile.TemporaryDirectory(prefix=prefix)
        self.tmpfile = tempfile.mktemp()
        self.script = script.TemporaryScript(
            'success.sh',
            SCRIPT_CONTENT % self.tmpfile,
            'avocado_wrapper_functional')
        self.script.save()
        self.dummy = script.TemporaryScript(
            'dummy.sh',
            DUMMY_CONTENT,
            'avocado_wrapper_functional')
        self.dummy.save()

    @unittest.skipIf(missing_binary('cc'),
                     "C compiler is required by the underlying datadir.py test")
    def test_global_wrapper(self):
        os.chdir(BASEDIR)
        cmd_line = ('%s run --job-results-dir %s --sysinfo=off --wrapper %s '
                    'examples/tests/datadir.py'
                    % (AVOCADO, self.tmpdir.name, self.script.path))
        result = process.run(cmd_line, ignore_status=True)
        expected_rc = exit_codes.AVOCADO_ALL_OK
        self.assertEqual(result.exit_status, expected_rc,
                         "Avocado did not return rc %d:\n%s" %
                         (expected_rc, result))
        self.assertTrue(os.path.exists(self.tmpfile),
                        "Wrapper did not touch the tmp file %s\nStdout: "
                        "%s\nCmdline: %s" %
                        (self.tmpfile, result.stdout, cmd_line))

    @unittest.skipIf(missing_binary('cc'),
                     "C compiler is required by the underlying datadir.py test")
    def test_process_wrapper(self):
        os.chdir(BASEDIR)
        cmd_line = ('%s run --job-results-dir %s --sysinfo=off '
                    '--wrapper %s:*/datadir examples/tests/datadir.py'
                    % (AVOCADO, self.tmpdir.name, self.script.path))
        result = process.run(cmd_line, ignore_status=True)
        expected_rc = exit_codes.AVOCADO_ALL_OK
        self.assertEqual(result.exit_status, expected_rc,
                         "Avocado did not return rc %d:\n%s" %
                         (expected_rc, result))
        self.assertTrue(os.path.exists(self.tmpfile),
                        "Wrapper did not touch the tmp file %s\nStdout: "
                        "%s\nStdout: %s" %
                        (self.tmpfile, cmd_line, result.stdout))

    @unittest.skipIf(missing_binary('cc'),
                     "C compiler is required by the underlying datadir.py test")
    def test_both_wrappers(self):
        os.chdir(BASEDIR)
        cmd_line = ('%s run --job-results-dir %s --sysinfo=off --wrapper %s '
                    '--wrapper %s:*/datadir examples/tests/datadir.py'
                    % (AVOCADO, self.tmpdir.name, self.dummy.path,
                       self.script.path))
        result = process.run(cmd_line, ignore_status=True)
        expected_rc = exit_codes.AVOCADO_ALL_OK
        self.assertEqual(result.exit_status, expected_rc,
                         "Avocado did not return rc %d:\n%s" %
                         (expected_rc, result))
        self.assertTrue(os.path.exists(self.tmpfile),
                        "Wrapper did not touch the tmp file %s\nStdout: "
                        "%s\nStdout: %s" %
                        (self.tmpfile, cmd_line, result.stdout))

    def tearDown(self):
        self.script.remove()
        self.dummy.remove()
        try:
            os.remove(self.tmpfile)
        except OSError:
            pass
        self.tmpdir.cleanup()


if __name__ == '__main__':
    unittest.main()
