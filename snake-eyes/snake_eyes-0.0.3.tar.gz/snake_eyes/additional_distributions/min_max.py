from typing import Generic, TypeVar, Iterable, Optional

import numpy as np

from snake_eyes.additional_distributions.split import JoinedSupportSpace
from snake_eyes.buffered_distribution import BufferedDistribution
from snake_eyes.bufferer import Bufferer
from snake_eyes.distribution import Distribution
from snake_eyes.support_space import SupportSpace
from snake_eyes.util import _maybe_parenthesise, prod

T = TypeVar('T')


def min_support_space(parts: Iterable[SupportSpace]):
    maxes = [p.maximum() for p in parts]
    partial_maxes = [
        min(m for (i, m) in maxes if i != j)
        for j, _ in enumerate(parts)
    ]
    return JoinedSupportSpace.join(
        p.truncate(None, m) for (p, m) in zip(parts, partial_maxes)
    )


class MinDistribution(Distribution[T], Generic[T]):
    def __init__(self, parts: Iterable[Distribution]):
        self.parts = tuple(parts)

    def get(self) -> T:
        return min(p.get() for p in self.parts)

    def cumulative_density(self, k) -> Optional[float]:
        inv_ret = 1
        for p in self.parts:
            cdf = p.cumulative_density(k)
            if cdf is None:
                return None
            inv_ret *= (1 - cdf)
        return 1 - inv_ret

    def support_space(self) -> Optional[SupportSpace]:
        ss = []
        for p in self.parts:
            s = p.support_space()
            if s is None:
                return None
            ss.append(s)
        return min_support_space(ss)

    def probability(self, k) -> Optional[float]:
        cdf = [
            p.cumulative_density(k) for p in self.parts
        ]
        prob = [
            p.probability(k) for p in self.parts
        ]
        if any(x is None for x in cdf) or any(x is None for x in prob):
            return None
        inv_cdf = [1 - x for x in cdf]
        prod_inv_cdf = prod(inv_cdf)
        return sum(
            (prod_inv_cdf / icdf) * p for (icdf, p) in zip(inv_cdf, prob)
        )

    def sample_cumulative_density(self, k, **kwargs) -> Optional[float]:
        inv_ret = 1
        for p in self.parts:
            cdf = p.approx_cumulative_density(k, **kwargs)
            inv_ret *= (1 - cdf)
        return 1 - inv_ret

    def sample_probability(self, k, sample_size=4096, epsilon=None) -> Optional[float]:
        cdf = [
            p.approx_cumulative_density(k, sample_size=sample_size) for p in self.parts
        ]
        prob = [
            p.approx_probability(k, sample_size=sample_size, epsilon=epsilon) for p in self.parts
        ]
        inv_cdf = [1 - x for x in cdf]
        prod_inv_cdf = prod(inv_cdf)
        return sum(
            (prod_inv_cdf / icdf) * p for (icdf, p) in zip(inv_cdf, prob)
        )

    def __str__(self):
        return type(self).__name__ + '(' \
               + ", ".join(_maybe_parenthesise(p) for p in self.parts) \
               + ')'

    def __eq__(self, other):
        return type(self) is type(other) \
               and set(self.parts) == set(self.parts)

    def __hash__(self):
        return hash((type(self), frozenset(self.parts)))


class MinBufferer(Bufferer):
    def __init__(self, parts: Iterable[Bufferer]):
        super().__init__()
        self.parts = tuple(parts)

    def get_buffer(self, size) -> np.ndarray:
        return np.min([p.get_buffer(size) for p in self.parts], axis=0)


class MinBufferedDistribution(BufferedDistribution[T], MinDistribution[T], Generic[T]):
    def __init__(self, parts: Iterable[BufferedDistribution[T]]):
        MinDistribution.__init__(self, parts)
        BufferedDistribution.__init__(self, MinBufferer(p.bufferer for p in parts))


def dmin(*parts: Distribution):
    if all(isinstance(p, BufferedDistribution) for p in parts):
        return MinBufferedDistribution(parts)
    return MinDistribution(parts)


def dmax(*parts: Distribution):
    return -dmin(*(-p for p in parts))
