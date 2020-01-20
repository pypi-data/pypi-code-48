# pylint: disable=unused-import
import argparse
import pybullet
import pybullet_envs
from all.environments import GymEnvironment
from all.experiments import Experiment
from all.presets import continuous

# some example envs
# can also enter ID directly
ENVS = {
    # classic continuous environments
    "mountaincar": "MountainCarContinuous-v0",
    "lander": "LunarLanderContinuous-v2",
    # Bullet robotics environments
    "ant": "AntBulletEnv-v0",
    "cheetah": "HalfCheetahBulletEnv-v0",
    "humanoid": "HumanoidBulletEnv-v0",
    "hopper": "HopperBulletEnv-v0",
    "walker": "Walker2DBulletEnv-v0"
}


def run():
    parser = argparse.ArgumentParser(description="Run a continuous actions benchmark.")
    parser.add_argument("env", help="Name of the env (see envs)")
    parser.add_argument(
        "agent",
        help="Name of the agent (e.g. actor_critic). See presets for available agents.",
    )
    parser.add_argument(
        "--frames", type=int, default=2e6, help="The number of training frames"
    )
    parser.add_argument(
        "--device",
        default="cuda",
        help="The name of the device to run the agent on (e.g. cpu, cuda, cuda:0)",
    )
    parser.add_argument(
        "--render", default=False, help="Whether to render the environment."
    )
    args = parser.parse_args()

    if args.env in ENVS:
        env_id = ENVS[args.env]
    else:
        env_id = args.env

    env = GymEnvironment(env_id, device=args.device)
    agent_name = args.agent
    agent = getattr(continuous, agent_name)

    Experiment(
        agent(device=args.device), env, frames=args.frames, render=args.render
    )


if __name__ == "__main__":
    run()
