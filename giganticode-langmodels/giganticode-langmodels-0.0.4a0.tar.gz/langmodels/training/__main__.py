import sys
import comet_ml

from langmodels.training.cli import run
from langmodels.repository import load_default_model

if __name__ == '__main__':
    run(sys.argv[1:])

    load_default_model()
    # run(['train',
    #      '-c', '/Users/hlib/dev/langmodels/default_config.json',
    #      '-p', 'training_procedure.schedule.init_lr:0.09', '--fallback-to-cpu'])
