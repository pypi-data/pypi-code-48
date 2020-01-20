from itertools import chain
from numbers import Rational
from typing import Generic, TypeVar, Iterable, Tuple, Any, Union, Optional

import numpy as np

from snake_eyes.support_space import SupportSpace, DistributionKind
from snake_eyes.buffered_distribution import ChoiceDistribution
from snake_eyes.distribution import Distribution, add, mul
from snake_eyes.util import common_dtype, _maybe_parenthesise

T = TypeVar('T')


class JoinedSupportSpace(SupportSpace):
    """
    Compound joining of support spaces
    """

    def __init__(self, parts: Iterable[SupportSpace]):
        self.parts = parts

    def kind(self) -> Optional[DistributionKind]:
        ret = None
        for p in self.parts:
            k = p.kind()
            if k is None or k == DistributionKind.Continuous:
                return None
            if ret is None:
                ret = k
            elif ret != k:
                return None
        return ret

    def truncate(self, a, b):
        parts_left = []
        for p in self.parts:
            parts_left.append(p.truncate(a, b))
        if all(p is None for p in parts_left):
            return None
        return type(self)(parts_left)

    def is_finite(self):
        return all(p.is_finite() for p in self.parts)

    @classmethod
    def join(cls, parts):
        uncontained = []
        parts = list(parts)
        while parts:
            part = parts.pop()
            if part is None:
                continue
            if all(not p.contains_space(part) for p in parts):
                uncontained.append(part)
        return cls(parts)

    def minimum(self):
        return min(p.minimum() for p in self.parts)

    def maximum(self):
        return max(p.maximum() for p in self.parts)

    def contains(self, k) -> bool:
        return any(p.contains(k) for p in self.parts)

    def __add__(self, other: Rational):
        return type(self)(tuple(p + other for p in self.parts))

    def __mul__(self, other: Rational):
        return type(self)(tuple(p * other for p in self.parts))

    def __iter__(self):
        infinite = []
        non_discrete = []
        continuous = []
        for p in self.parts:
            if p.is_finite():
                yield from p
            elif p.kind() == DistributionKind.Continuous:
                continuous.append(p)
            elif p.kind() == DistributionKind.Discrete:
                infinite.append(p)
            else:
                non_discrete.append(p)
        yield from chain.from_iterable(infinite)
        yield from chain.from_iterable(non_discrete)
        yield from chain.from_iterable(continuous)


class SplitDistribution(Distribution[T], Generic[T]):
    """
    A distribution that has a chance to delegate other distributions
    """

    def __init__(self, options: Iterable[Distribution[T]], probabilites: Iterable[float]):
        self.options: Tuple[Distribution[T]] = tuple(options)
        self.probabilities = tuple(probabilites)
        self.index_distribution = ChoiceDistribution(range(len(self.options)), p=self.probabilities)

    @classmethod
    def create(cls, options: Iterable[Tuple[Any, Union[type(...), float]]], normalize=False):
        partial_total = 0
        dists = []
        probs = []
        for (d, p) in options:
            dists.append(cls.coerce(d))
            if p is ...:
                if normalize:
                    raise ValueError('cannot use normalize and ... together')
                p = 1 - partial_total
            if p == 0:
                continue
            if p < 0:
                raise ValueError(f'option {d} had negative probability')
            probs.append(p)
            partial_total += p
            if not normalize and partial_total > 1:
                raise ValueError('total probabilities exceed 1')
        if normalize:
            probs = (p / partial_total for p in probs)
        return cls(dists, probs)

    def get(self):
        return self.options[self.index_distribution.get()].get()

    def get_n(self, n):
        indices = np.asanyarray(self.index_distribution.get_n(n))
        individuals = [
            np.asanyarray(option.get_n(np.sum(indices == i)))
            for (i, option) in enumerate(self.options)
        ]
        dtype = common_dtype(*individuals)
        ret = np.empty(shape=n, dtype=dtype)
        for i in range(len(individuals)):
            ret[indices == i] = individuals[i]
        return ret

    def mean(self):
        ret = 0
        for o, p in zip(self.options, self.probabilities):
            m = o.mean()
            if m is None:
                return None
            ret += (m * p)
        return ret

    def variance(self):
        mean = self.mean()
        if mean is None:
            return None
        ret = mean ** 2
        for p, sub_dist in zip(self.probabilities, self.options):
            subdist_mean = sub_dist.mean()
            if subdist_mean is None:
                return None
            subdist_var = sub_dist.variance()
            if subdist_var is None:
                return None
            subdist_mean_sq = subdist_var + subdist_mean ** 2
            ret += p * (subdist_mean_sq - 2 * mean * subdist_mean)

        return ret

    def support_space(self):
        ss = tuple(p.support_space() for p in self.options)
        if None in ss:
            return None
        return JoinedSupportSpace.join(ss)

    def cumulative_density(self, k):
        ret = 0
        for (o, p) in zip(self.options, self.probabilities):
            m = o.cumulative_density(k)
            if m is None:
                return None
            ret += p * m
        return ret

    def probability(self, k):
        ret = 0
        for (o, p) in zip(self.options, self.probabilities):
            m = o.probability(k)
            if m is None:
                return None
            ret += p * m
        return ret

    def __neg__(self):
        return type(self)(
            (-s for s in self.options),
            self.probabilities
        )

    def reciprocal(self):
        return type(self)(
            (s.reciprocal() for s in self.options),
            self.probabilities
        )

    @add.implementor(symmetric=True)
    def add(self, other: Any):
        return type(self)(
            (s + other for s in self.options),
            self.probabilities
        )

    @mul.implementor(symmetric=True)
    def mul(self, other: Any):
        return type(self)(
            (s * other for s in self.options),
            self.probabilities
        )

    def truncate(self, min=None, max=None):
        return type(self)(
            (s.truncate(min, max) for s in self.options),
            self.probabilities
        )

    def __str__(self):
        return type(self).__name__ + '(' \
               + ", ".join(f"{p:.1%}: {_maybe_parenthesise(c)}" for (c, p) in zip(self.options, self.probabilities)) \
               + ')'

    def __eq__(self, other):
        return type(self) is type(other) \
               and set(zip(self.options, self.probabilities)) == set(zip(other.options, other.probabilites))

    def __hash__(self):
        return hash((type(self), frozenset(zip(self.options, self.probabilities))))
