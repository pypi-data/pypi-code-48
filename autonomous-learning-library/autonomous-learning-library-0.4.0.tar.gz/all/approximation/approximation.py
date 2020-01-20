import os
import torch
from torch.nn import utils
from all.logging import DummyWriter
from .target import TrivialTarget
from .checkpointer import PeriodicCheckpointer

DEFAULT_CHECKPOINT_FREQUENCY = 200

class Approximation():
    '''
    Base function approximation object.

    This defines a Pytorch-based function approximation object that
    wraps key functionality useful for reinforcement learning, including
    decaying learning rates, model checkpointing, loss scaling, gradient
    clipping, target networks, and tensorboard logging. This enables
    increased code reusability and simpler Agent implementations.

    Args:
            model (:torch.nn.Module:): A Pytorch module representing the model
                used to approximate the function. This could be a convolution
                network, a fully connected network, or any other Pytorch-compatible
                model.
            optimizer (:torch.optim.Optimizer:): A optimizer initialized with the
                model parameters, e.g. SGD, Adam, RMSprop, etc.
            checkpointer: (:all.approximation.checkpointer.Checkpointer): A Checkpointer object
                that periodically saves the model and its parameters to the disk. Default:
                A PeriodicCheckpointer that saves the model once every 200 updates.
            clip_grad: (float, optional): If non-zero, clips the norm of the
                gradient to this value in order prevent large updates and
                improve stability.
                See torch.nn.utils.clip_grad.
            loss_scaling: (float, optional): Multiplies the loss by this value before
                performing a backwards pass. Useful when used with multi-headed networks
                with shared feature layers.
            name: (str, optional): The name of the function approximator used for logging.
            scheduler: (:torch.optim.lr_scheduler._LRScheduler:, optional): A learning
                rate scheduler initialized with the given optimizer. step() will be called
                after every update.
            target: (:all.approximation.target.TargetNetwork, optional): A target network object
                to be used during optimization. A target network updates more slowly than
                the base model that is being optimizing, allowing for a more stable
                optimization target.
            writer: (:all.logging.Writer:, optional): A Writer object used for logging.
                The standard object logs to tensorboard, however, other types of Writer objects
                may be implemented by the user.
    '''
    def __init__(
            self,
            model,
            optimizer,
            checkpointer=None,
            clip_grad=0,
            loss_scaling=1,
            name='approximation',
            scheduler=None,
            target=None,
            writer=DummyWriter(),
    ):
        self.model = model
        self.device = next(model.parameters()).device
        self._target = target or TrivialTarget()
        self._scheduler = scheduler
        self._target.init(model)
        self._updates = 0
        self._optimizer = optimizer
        self._loss_scaling = loss_scaling
        self._cache = []
        self._clip_grad = clip_grad
        self._writer = writer
        self._name = name

        if checkpointer is None:
            checkpointer = PeriodicCheckpointer(DEFAULT_CHECKPOINT_FREQUENCY)
        self._checkpointer = checkpointer
        self._checkpointer.init(
            self.model,
            os.path.join(writer.log_dir, name + '.pt')
        )

    def __call__(self, *inputs):
        '''
        Run a forward pass of the model.
        '''
        return self.model(*inputs)

    def eval(self, *inputs):
        '''Run a forward pass of the model in no_grad mode.'''
        with torch.no_grad():
            return self.model(*inputs)

    def target(self, *inputs):
        '''Run a forward pass of the target network.'''
        return self._target(*inputs)

    def reinforce(self, loss):
        loss = self._loss_scaling * loss
        self._writer.add_loss(self._name, loss.detach())
        loss.backward()
        self.step()
        return self

    def step(self):
        '''Given that a backward pass has been made, run an optimization step.'''
        if self._clip_grad != 0:
            utils.clip_grad_norm_(self.model.parameters(), self._clip_grad)
        self._optimizer.step()
        self._optimizer.zero_grad()
        self._target.update()
        if self._scheduler:
            self._writer.add_schedule(self._name + '/lr', self._optimizer.param_groups[0]['lr'])
            self._scheduler.step()
        self._checkpointer()
        return self

    def zero_grad(self):
        self._optimizer.zero_grad()
        return self
