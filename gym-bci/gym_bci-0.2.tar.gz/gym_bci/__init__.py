from gym.envs.registration import register

register(
    id='bci-arrows-v0',
    entry_point='gym_bci.envs:ArrowsEnv',
)

register(
    id='bci-pacman-v0',
    entry_point='gym_bci.envs:PacmanEnv',
)
