from corens.ns import *
from corens.mod import I, nsImport
from corens.tpl import nsTemplate, nsMk
from corens.cfg_grammar import nsCfgFSLoad
from corens.cfg_grammar import nsCfgLoad
from corens.log import *
from corens.arrghs import *
from corens.help import *
from corens.console import *
from corens.version import nsVersion, nsRelease


def n(ns):
    return ns

_lib = {
    '/bin/mkdir': nsMkdir,
    '/bin/get': nsGet,
    '/bin/set': nsSet,
    '/bin/ls': nsLs,
    '/bin/ns': n,
    '/bin/V': V,
    '/bin/I': I,
    '/bin/import': nsImport,
    '/bin/T': nsTemplate,
    '/bin/Mk': nsMk,
    '/bin/C': nsCfgLoad,
    '/bin/Cfg': nsCfgFSLoad,
    '/bin/debug': nsDebug,
    '/bin/info': nsInfo,
    '/bin/warning': nsWarning,
    '/bin/error': nsError,
    '/bin/critical': nsCritical,
    '/bin/panic': nsPanic,
    '/bin/logsize': nsLogSize,
    '/sbin/logprocessor': nsLogProcess,
    '/bin/args': nsArgs,
    '/bin/cmd': nsCmd,
    '/bin/help': nsHelp,
    '/bin/console': nsConsole,
    '/sbin/consoleprocessor': nsConsoleProcess,
    '/sbin/corens_version': nsVersion,
    '/sbin/corens_release': nsRelease,
}
