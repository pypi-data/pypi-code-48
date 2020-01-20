from datetime import datetime
import os.path as op
import logging as log

class Command(object):
    def __init__(self, command, args, xnat_instance, destdir, overwrite):
        self.command = command
        self.args = args
        self.xnat = xnat_instance
        self.destdir = destdir
        self.overwrite = overwrite

    def run_id(self, id, func, **kwargs):
        from bx import xnat

        max_rows = None
        if 'max_rows' in kwargs:
            max_rows = kwargs['max_rows']
            kwargs.pop('max_rows')

        experiments = xnat.collect_experiments(self.xnat, id, max_rows=max_rows)
        return func(self.xnat, experiments, **kwargs)

    def to_excel(self, id, df):
        dt = datetime.today().strftime('%Y%m%d_%H%M%S')
        fn = 'bx_%s_%s_%s.xlsx'%(self.command, id, dt)
        fp = op.join(self.destdir, fn)
        log.info('Saving it in %s'%fp)
        df.to_excel(fp)
