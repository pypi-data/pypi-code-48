import sys
from ejcli.http import submission_status
from ejcli.error import EJError

def still_running(s):
    return s.endswith('...') or ', ' in s or s in ('Compiling', 'Running', 'Judging', 'Check failed', 'Available for testing', 'Full rejudge', 'Pending check', 'Pending judgement', 'Queue judge')

def do_astatus(self, cmd):
    """
    usage: astatus <subm_id>

    Fancy testing progress display
    """
    subm_id = cmd.strip() 
    if not subm_id.isnumeric():
        return self.do_help('astatus')
    chars = '\\|/-'
    idx = 0
    prev = ''
    while True:
        cur = submission_status(self.url, self.cookie, int(subm_id))
        if cur == None:
            raise EJError('No such submission')
        cur = cur.strip()
        sys.stderr.write(' '*len(prev)+'\r')
        sys.stderr.flush()
        if still_running(cur):
            prev = '%%%ds' % len(prev) % (cur + ' ' + chars[idx])
            idx = (idx + 1) % 4
#           print(prev)
            sys.stderr.write(prev+'\r')
            sys.stderr.flush()
        else:
            print(cur)
            break
