from itertools import dropwhile, takewhile
from pathlib import Path
import inspect
import logging
import os

import wrapt

LOG_LEVEL = os.environ.get('LOG_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOG_LEVEL)
LOGGER = logging.getLogger(__name__)
# ------------------------------------------------------------------------------

'''
Imports only python builtins and contains only function for use within or
outside of Docker environment (ie no dependencies or specific python versions.)
'''


def relative_path(module, path):
    '''
    Resolve path given current module's file path and given suffix.

    Args:
        module (str): Always __file__ of current module.
        path (str): Path relative to __file__.

    Returns:
        Path: Resolved Path object.
    '''
    module_root = Path(module).parent
    path = Path(path).parts
    path = list(dropwhile(lambda x: x == ".", path))
    up = len(list(takewhile(lambda x: x == "..", path)))
    path = Path(*path[up:])
    root = list(module_root.parents)[up - 1]
    output = Path(root, path).absolute()

    LOGGER.debug(
        f'relative_path called with: {module} and {path}. Returned: {output}')
    return output


def get_function_signature(function):
    '''
    Inspect a given function and return its arguments as a list and its keyword
    arguments as a dict.

    Args:
        function (function): Function to be inspected.

    Returns:
        dict: args and kwargs.
    '''
    spec = inspect.getfullargspec(function)
    args = list(spec.args)
    kwargs = {}
    if spec.defaults is not None:
        args = args[:-len(spec.defaults)]
        kwargs = list(spec.args)[-len(spec.defaults):]
        kwargs = dict(zip(kwargs, spec.defaults))
    return dict(args=args, kwargs=kwargs)


def api_function(wrapped=None, **kwargs):
    '''
    A decorator that enforces keyword argument only function signatures and
    required keyword argument values when called.

    Args:
        wrapped (function): For dev use. Default: None.
        \*\*kwargs (dict): Keyword arguments. # noqa: W605

    Raises:
        TypeError: If non-keyword argument found in functionn signature.
        ValueError: If keyword arg with value of '<required>' is found.

    Returns:
        api function.
    '''
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        sig = get_function_signature(wrapped)

        # ensure no arguments are present
        if len(sig['args']) > 0:
            msg = 'Function may only have keyword arguments. '
            msg += f"Found non-keyword arguments: {sig['args']}."
            raise TypeError(msg)

        # ensure all required kwarg values are present
        params = sig['kwargs']
        params.update(kwargs)
        for key, val in params.items():
            if val == '<required>':
                msg = f'Missing required keyword argument: {key}.'
                raise ValueError(msg)

        LOGGER.debug(f'{wrapped} called with {params}.')
        return wrapped(*args, **kwargs)
    return wrapper(wrapped)


def is_standard_module(name):
    '''
    Determines if given module name is a python builtin.

    Args:
        name (str): Python module name.

    Returns:
        bool: Whether string names a python module.
    '''
    return name in _PYTHON_STANDARD_MODULES


_PYTHON_STANDARD_MODULES = [
    '__future__',
    '__main__',
    '_dummy_thread',
    '_thread',
    'abc',
    'aifc',
    'argparse',
    'array',
    'ast',
    'asynchat',
    'asyncio',
    'asyncore',
    'atexit',
    'audioop',
    'base64',
    'bdb',
    'binascii',
    'binhex',
    'bisect',
    'builtins',
    'bz2',
    'calendar',
    'cgi',
    'cgitb',
    'chunk',
    'cmath',
    'cmd',
    'code',
    'codecs',
    'codeop',
    'collections',
    'collections.abc',
    'colorsys',
    'compileall',
    'concurrent',
    'concurrent.futures',
    'configparser',
    'contextlib',
    'contextvars',
    'copy',
    'copyreg',
    'cProfile',
    'crypt',
    'csv',
    'ctypes',
    'curses',
    'curses.ascii',
    'curses.panel',
    'curses.textpad',
    'dataclasses',
    'datetime',
    'dbm',
    'dbm.dumb',
    'dbm.gnu',
    'dbm.ndbm',
    'decimal',
    'difflib',
    'dis',
    'distutils',
    'distutils.archive_util',
    'distutils.bcppcompiler',
    'distutils.ccompiler',
    'distutils.cmd',
    'distutils.command',
    'distutils.command.bdist',
    'distutils.command.bdist_dumb',
    'distutils.command.bdist_msi',
    'distutils.command.bdist_packager',
    'distutils.command.bdist_rpm',
    'distutils.command.bdist_wininst',
    'distutils.command.build',
    'distutils.command.build_clib',
    'distutils.command.build_ext',
    'distutils.command.build_py',
    'distutils.command.build_scripts',
    'distutils.command.check',
    'distutils.command.clean',
    'distutils.command.config',
    'distutils.command.install',
    'distutils.command.install_data',
    'distutils.command.install_headers',
    'distutils.command.install_lib',
    'distutils.command.install_scripts',
    'distutils.command.register',
    'distutils.command.sdist',
    'distutils.core',
    'distutils.cygwinccompiler',
    'distutils.debug',
    'distutils.dep_util',
    'distutils.dir_util',
    'distutils.dist',
    'distutils.errors',
    'distutils.extension',
    'distutils.fancy_getopt',
    'distutils.file_util',
    'distutils.filelist',
    'distutils.log',
    'distutils.msvccompiler',
    'distutils.spawn',
    'distutils.sysconfig',
    'distutils.text_file',
    'distutils.unixccompiler',
    'distutils.util',
    'distutils.version',
    'doctest',
    'dummy_threading',
    'email',
    'email.charset',
    'email.contentmanager',
    'email.encoders',
    'email.errors',
    'email.generator',
    'email.header',
    'email.headerregistry',
    'email.iterators',
    'email.message',
    'email.mime',
    'email.parser',
    'email.policy',
    'email.utils',
    'encodings',
    'encodings.idna',
    'encodings.mbcs',
    'encodings.utf_8_sig',
    'ensurepip',
    'enum',
    'errno',
    'faulthandler',
    'fcntl',
    'filecmp',
    'fileinput',
    'fnmatch',
    'formatter',
    'fractions',
    'ftplib',
    'functools',
    'gc',
    'getopt',
    'getpass',
    'gettext',
    'glob',
    'grp',
    'gzip',
    'hashlib',
    'heapq',
    'hmac',
    'html',
    'html.entities',
    'html.parser',
    'http',
    'http.client',
    'http.cookiejar',
    'http.cookies',
    'http.server',
    'imaplib',
    'imghdr',
    'imp',
    'importlib',
    'importlib.abc',
    'importlib.machinery',
    'importlib.resources',
    'importlib.util',
    'inspect',
    'io',
    'ipaddress',
    'itertools',
    'json',
    'json.tool',
    'keyword',
    'lib2to3',
    'linecache',
    'locale',
    'logging',
    'logging.config',
    'logging.handlers',
    'lzma',
    'macpath',
    'mailbox',
    'mailcap',
    'marshal',
    'math',
    'mimetypes',
    'mmap',
    'modulefinder',
    'msilib',
    'msvcrt',
    'multiprocessing',
    'multiprocessing.connection',
    'multiprocessing.dummy',
    'multiprocessing.managers',
    'multiprocessing.pool',
    'multiprocessing.sharedctypes',
    'netrc',
    'nis',
    'nntplib',
    'numbers',
    'operator',
    'optparse',
    'os',
    'os.path',
    'ossaudiodev',
    'parser',
    'pathlib',
    'pdb',
    'pickle',
    'pickletools',
    'pipes',
    'pkgutil',
    'platform',
    'plistlib',
    'poplib',
    'posix',
    'pprint',
    'profile',
    'pstats',
    'pty',
    'pwd',
    'py_compile',
    'pyclbr',
    'pydoc',
    'queue',
    'quopri',
    'random',
    're',
    'readline',
    'reprlib',
    'resource',
    'rlcompleter',
    'runpy',
    'sched',
    'secrets',
    'select',
    'selectors',
    'shelve',
    'shlex',
    'shutil',
    'signal',
    'site',
    'smtpd',
    'smtplib',
    'sndhdr',
    'socket',
    'socketserver',
    'spwd',
    'sqlite3',
    'ssl',
    'stat',
    'statistics',
    'string',
    'stringprep',
    'struct',
    'subprocess',
    'sunau',
    'symbol',
    'symtable',
    'sys',
    'sysconfig',
    'syslog',
    'tabnanny',
    'tarfile',
    'telnetlib',
    'tempfile',
    'termios',
    'test',
    'test.support',
    'test.support.script_helper',
    'textwrap',
    'threading',
    'time',
    'timeit',
    'tkinter',
    'tkinter.scrolledtext',
    'tkinter.tix',
    'tkinter.ttk',
    'token',
    'tokenize',
    'trace',
    'traceback',
    'tracemalloc',
    'tty',
    'turtle',
    'turtledemo',
    'types',
    'typing',
    'unicodedata',
    'unittest',
    'unittest.mock',
    'urllib',
    'urllib.error',
    'urllib.parse',
    'urllib.request',
    'urllib.response',
    'urllib.robotparser',
    'uu',
    'uuid',
    'venv',
    'warnings',
    'wave',
    'weakref',
    'webbrowser',
    'winreg',
    'winsound',
    'wsgiref',
    'wsgiref.handlers',
    'wsgiref.headers',
    'wsgiref.simple_server',
    'wsgiref.util',
    'wsgiref.validate',
    'xdrlib',
    'xml',
    'xml.dom',
    'xml.dom.minidom',
    'xml.dom.pulldom',
    'xml.etree.ElementTree',
    'xml.parsers.expat',
    'xml.parsers.expat.errors',
    'xml.parsers.expat.model',
    'xml.sax',
    'xml.sax.handler',
    'xml.sax.saxutils',
    'xml.sax.xmlreader',
    'xmlrpc',
    'xmlrpc.client',
    'xmlrpc.server',
    'zipapp',
    'zipfile',
    'zipimport',
    'zlib'
]
