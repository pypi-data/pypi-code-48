from torch.optim import Adam
from all.agents import VQN
from all.approximation import QNetwork
from all.policies import GreedyPolicy
from all.logging import DummyWriter
from .models import fc_relu_q

def vqn(
        # Common settings
        device="cpu",
        discount_factor=0.99,
        # Adam optimizer settings
        lr=1e-2,
        eps=1e-5,
        # Exploration settings
        epsilon=0.1,
        # Parallel actors
        n_envs=1,
):
    """
    Vanilla Q-Network classic control preset.

    Args:
        device (str): The device to load parameters and buffers onto for this agent.
        discount_factor (float): Discount factor for future rewards.
        lr (float): Learning rate for the Adam optimizer.
        eps (float): Stability parameters for the Adam optimizer.
        epsilon (int): Probability of choosing a random action.
        n_envs (int): Number of parallel environments.
    """
    def _vqn(envs, writer=DummyWriter()):
        env = envs[0]
        model = fc_relu_q(env).to(device)
        optimizer = Adam(model.parameters(), lr=lr, eps=eps)
        q = QNetwork(model, optimizer, writer=writer)
        policy = GreedyPolicy(q, env.action_space.n, epsilon=epsilon)
        return VQN(q, policy, discount_factor=discount_factor)
    return _vqn, n_envs
 