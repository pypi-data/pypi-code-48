from .api import Api
from IPython.core.display import display, HTML


def init(project=None):
    """Initialize W&B

    If called from within Jupyter, initializes a new run and waits for a call to
    `wbclione.log` to begin pushing metrics.  Otherwise, spawns a new process
    to communicate with W&B.

    Args:
        job_type (str, optional): The type of job running, defaults to 'train'
        config (dict, argparse, or tf.FLAGS, optional): The hyper parameters to store with the run
        project (str, optional): The project to push metrics to
        entity (str, optional): The entity to push metrics to
        dir (str, optional): An absolute path to a directory where metadata will be stored
        group (str, optional): A unique string shared by all runs in a given group
        tags (list, optional): A list of tags to apply to the run
        id (str, optional): A globally unique (per project) identifier for the run
        name (str, optional): A display name which does not have to be unique
        notes (str, optional): A multiline string associated with the run
        reinit (bool, optional): Allow multiple calls to init in the same process
        resume (bool, str, optional): Automatically resume this run if run from the same machine,
            you can also pass a unique run_id
        sync_tensorboard (bool, optional): Synchronize wbclione logs to tensorboard or tensorboardX
        force (bool, optional): Force authentication with wbclione, defaults to False
        magic (bool, dict, or str, optional): magic configuration as bool, dict, json string,
            yaml filename
        anonymous (str, optional): Can be "allow", "must", or "never". Controls whether anonymous logging is allowed.
            Defaults to never.

    Returns:
        A wbclione.run object for metric and config logging.
    """
    api = Api()
    if project == None:
      return

    global run

    run = api.create_run(project=project)

    return run



def log(row=None, commit=True, step=None, sync=True, *args, **kwargs):
  """Log a dict to the global run's history.

  wbclione.log({'train-loss': 0.5, 'accuracy': 0.9})

  Args:
      row (dict, optional): A dict of serializable python objects i.e str: ints, floats, Tensors, dicts, or wbclione.data_types
      commit (boolean, optional): Persist a set of metrics, if false just update the existing dict
      step (integer, optional): The global step in processing. This sets commit=True any time step increases
      sync (boolean, True): If set to False, process calls to log in a seperate thread
  """
  api = Api()
  if run is None:
      raise ValueError(
          "You must call `wbclione.init` in the same process before calling log")
  
  display(HTML('''Row: {}'''.format(row)))

  api.create_log(run, row)
  display(HTML('''Logging results to server.'''))

