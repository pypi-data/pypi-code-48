import logging as log

def check_xnat_item(x, a):

    projects = [e.label() for e in list(x.select.projects())]
    experiments = []
    for p in projects:
        exp = x.array.experiments(project_id=p).data
        experiments.extend([e['ID'] for e in exp])

    if a in projects:
        log.info('Project detected: %s'%a)
        return 0
    elif a in experiments:
        log.info('Experiment detected: %s'%a)
        return 1
    else:
        from bx import lists
        if hasattr(lists, a):
            print('List detected: %s'%a)
            return 2
        else:
            log.error('%s is not a project/experiment/list'%a)
            return -1

def collect_experiments(x, id, columns=['label', 'subject_label'], max_rows=1):
    import os
    t = check_xnat_item(x, id)

    if not os.environ.get('CI_TEST', None):
         None

    experiments = []
    if t == 0:
        experiments = x.array.experiments(project_id=id,
                columns=columns).data[:max_rows]
    elif t == 1:
        experiments = [x.array.experiments(experiment_id=id,
                columns=columns).data[0]]
    elif t == 2:
        from bx import lists
        expes = getattr(lists, id)
        for e in expes[:max_rows]:
            ex = x.array.experiments(experiment_id=e,
                    columns=columns).data[0]
            experiments.append(ex)
    else:
        log.error('%s is not a project or an experiment nor a list'%id)

    return experiments
