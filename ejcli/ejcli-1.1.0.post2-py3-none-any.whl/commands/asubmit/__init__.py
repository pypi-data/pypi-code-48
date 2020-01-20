from ejcli.http import submit, task_list, task_ids, submission_list, compiler_list, may_cache
from ejcli.error import EJError
import os.path, shlex

def get_lang_id(self, lang_name, task_id):
    try: task_id = task_ids(self.url, self.cookie)[task_id]
    except IndexError: raise EJError("No such task")
    lang_id = [i for i, j, k in compiler_list(self.url, self.cookie, task_id) if j == lang_name]
    try: lang_id, = lang_id
    except ValueError: raise EJError("Unknown language: "+lang_name)
    return lang_id

def get_possible_lang_id(self, lang_names, task_id):
    try: task_id = task_ids(self.url, self.cookie)[task_id]
    except IndexError: raise EJError("No such task.")
    lang_id = [i for i, j, k in compiler_list(self.url, self.cookie, task_id) if j in lang_names]
    lang_id.append(None)
    return lang_id[0]

def check_exists(fname, options=set()):
    return os.path.exists(fname) or '-exist' in options

def do_asubmit(self, cmd, afmt=False):
    """
    usage: asubmit [-w] [-x <extension>] <task> <lang_id> <file>

    Submit a new solution, using style-fixed version.
    Uses a specific style fixer if -x is specified.
    Waits until testing ends if -w is specified.
    """
    modname = ''
    wait = False
    sp = shlex.split(cmd)
    if len(sp) not in range(3, 7):
        return self.do_help('asubmit')
    if not afmt and sp[0] == '-w':
        wait = True
        del sp[0]
    if len(sp) not in (3, 5):
        return self.do_help('asubmit')
    if sp[0] == '-x':
        modname = sp[1]
        del sp[:2]
        if modname[:1] == '.': modname = 'ejcli.commands.asubmit.format_'+modname[1:]
    if len(sp) != (1 if afmt else 3):
        return self.do_help('asubmit')
    with may_cache(self.url, self.cookie):
        tasks = task_list(self.url, self.cookie)
        try: task_id = tasks.index(sp[0])
        except ValueError:
            raise EJError("No such task.")
        if not sp[1].isnumeric():
            sp[1] = get_lang_id(self, sp[1], task_id)
        try:
            name = sp[2]
            module = None
            ext = os.path.splitext(name)[1][1:]
            modname, *modargs = modname.split(',')
            modargs = set(modargs)
            if not modname: modname = 'ejcli.commands.asubmit.format_'+ext
            try:
                module = __import__(modname, fromlist=True)
            except ImportError: pass
            if not getattr(module, 'check_exists', check_exists)(name, modargs):
                raise EJError("File not found.")
            if hasattr(module, 'read_file'):
                data = module.read_file(name, modargs)
            else:
                with open(name, 'rb') as file:
                    data = file.read()
            if hasattr(module, 'format'):
                data = module.format(data, modargs)
        except UnicodeDecodeError:
            raise EJError("File is binary.")
        before = submission_list(self.url, self.cookie)[0]
        submit(self.url, self.cookie, task_id, int(sp[1]), data)
    after = submission_list(self.url, self.cookie)[0]
    if before == after:
        raise EJError("Error while sending.")
    else:
        print('Submission ID is', after[0])
        if wait: self.do_astatus(str(after[0]))
