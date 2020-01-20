from typing import TypeVar, Callable, Union, Container

from snake_eyes.support_space import DistributionKind
from snake_eyes.distribution import Distribution

T = TypeVar('T')


def explode(inner: Distribution[T], exploding_func: Union[Callable[[T], bool], Container[T]] = ...):
    if exploding_func is ...:
        ss = inner.support_space()
        if ss is None or ss.kind() != DistributionKind.Discrete:
            raise Exception('exploding_func must be declared for non-discrete distributions')
        m = ss.maximum()

        def exploding_func(x):
            return x == m
    elif isinstance(exploding_func, Callable):
        pass
    elif isinstance(exploding_func, Container):
        exploding_func = exploding_func.__contains__
    else:
        raise TypeError(f'cannot parse exploding_func {exploding_func}')

    ret = inner.map(
        lambda x: x + ret.get() if exploding_func(x) else x
    )
    return ret
