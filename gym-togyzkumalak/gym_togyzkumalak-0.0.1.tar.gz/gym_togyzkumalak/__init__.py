import logging
from gym.envs.registration import register

logger = logging.getLogger(__name__)

register(
    id='Togyzkumalak-v0',
    entry_point='gym_togyzkumalak.envs:TogyzkumalakEnv',
)
