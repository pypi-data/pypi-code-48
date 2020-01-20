import time
import uuid
from  gevent import queue
import fnmatch
from dpath.util import get as dget
from dpath.util import set as dset
from dpath.util import new as dnew


def NS(**kw):
    ns = {}
    nsMkdir(ns, "/sys")
    nsMkdir(ns, "/sys/log")
    nsMkdir(ns, "/sys/log/channels")
    nsMkdir(ns, "/config")
    nsMkdir(ns, "/etc")
    nsMkdir(ns, "/etc/args")
    nsMkdir(ns, "/help")
    nsMkdir(ns, "/help/cmd")
    nsMkdir(ns, "/bin")
    nsMkdir(ns, "/sbin")
    nsMkdir(ns, "/tmp")
    nsMkdir(ns, "/scripts")
    nsMkdir(ns, "/templates")
    nsMkdir(ns, "/home")
    nsMkdir(ns, "/usr/local/bin")
    nsMkdir(ns, "/dev")
    nsSet(ns, "/sys/error", False)
    nsSet(ns, "/sys/error.msg", None)
    nsSet(ns, "/sys/log/messages", queue.Queue())
    nsSet(ns, "/sys/console", queue.Queue())
    ns.update(kw)
    return ns

def nsGlobalError(ns, msg=None):
    nsSet(ns, "/sys/error", True)
    nsSet(ns, "/sys/error.msg", msg)

def nsErrorClear(ns):
    nsSet(ns, "/sys/error", False)
    nsSet(ns, "/sys/error.msg", None)

def nsMkdir(ns, path, **kw):
    try:
        d = dget(ns, "{}/__dir__".format(path))
        if d is not True:
            return None
    except KeyError:
        dnew(ns, path, kw)
        dnew(ns, "{}/__dir__".format(path), True)
        dnew(ns, "{}/__id__".format(path), str(uuid.uuid4()))
        dnew(ns, "{}/__name__".format(path), path)
    return nsGet(ns, path, None)

def nsGet(ns, path, default=None):
    try:
        return dget(ns, path)
    except KeyError:
        return default

def nsLs(ns, path):
    res = nsGet(ns, path, {})
    if '__dir__' in res and res.get('__dir__') != True:
        return {}
    for k in list(res.keys()):
        if fnmatch.fnmatch(k, "__*") is True:
            del res[k]
    return res


def nsSet(ns, key, val):
    try:
        v = dget(ns, key)
        if nsGet(ns, "/config/var.redefine", True) is True:
            dset(ns, key, val)
    except KeyError:
        dnew(ns, key, val)
    return ns

def V(ns, name, val=None):
    if name[0] != "/":
        name = "/home/{}".format(name)
    if val is None:
        return nsGet(ns, name)
    else:
        ns =  nsSet(ns, name, val)
        return nsGet(ns, name)
