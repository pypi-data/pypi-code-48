from abc import abstractmethod, ABC
from heapq import heapify, heappop
from typing import Generic, TypeVar, Optional

import numpy as np
from scipy.special import binom

from snake_eyes import DistributionKind
from snake_eyes.buffered_distribution import BufferedDistribution
from snake_eyes.bufferer import Bufferer
from snake_eyes.distribution import Distribution
from snake_eyes.support_space import SupportSpace, SumSupportSpace, ProdSupportSpace
from snake_eyes.util import prod

T = TypeVar('T')


class Drop(Distribution[T], Generic[T]):
    def __init__(self, inner: Distribution[T], total_rolls: int, drop_low: int = 0, drop_high: int = 0):
        self.inner = inner
        self.total_rolls = total_rolls
        self.drop_low = drop_low
        self.drop_high = drop_high

    @classmethod
    @abstractmethod
    def func(cls, parts):
        pass

    def get(self) -> T:
        heap = self.inner.get_n(self.total_rolls)
        if not isinstance(heap, list):
            heap = list(heap)
        heapify(heap)
        for _ in range(self.drop_low):
            heappop(heap)
        ret = []
        for _ in range(self.actual_parts()):
            ret.append(heappop(heap))
        return self.func(ret)

    def actual_parts(self):
        return self.total_rolls - self.drop_low - self.drop_high

    def cumulative_density(self, k) -> Optional[float]:
        if self.actual_parts() == 1:
            i_cdf = self.inner.cumulative_density(k)
            if i_cdf is None:
                return None
            return sum(
                binom(self.total_rolls, i) * i_cdf ** i * (1 - i_cdf) ** (T - i)
                for i in range(self.drop_low + 1, self.total_rolls + 1)
            )
        return super().cumulative_density(k)

    def probability(self, k) -> Optional[float]:
        if self.actual_parts() == 1:
            ss = self.inner.support_space()
            if ss is None:
                return None
            kind = ss.kind()
            if kind is None:
                return None
            i_cdf = self.inner.cumulative_density(k)
            i_pdf = self.inner.probability(k)
            if i_cdf is None or i_pdf is None:
                return None
            if kind == DistributionKind.Continuous:
                return (self.drop_low + 1) * i_pdf \
                       * binom(self.total_rolls, (self.drop_low + 1)) \
                       * (i_cdf ** self.drop_low) \
                       * (1 - i_cdf) ** (T - self.drop_low - 1)
            elif kind == DistributionKind.Discrete:
                sum(
                    binom(self.total_rolls, i) *
                    ((i_cdf ** i * (1 - i_cdf) ** (T - i))
                     - ((i_cdf - i_pdf) ** i * (1 - (i_cdf - i_pdf)) ** (T - i)))
                    for i in range(self.drop_low + 1, self.total_rolls + 1)
                )
            else:
                return None
        return super().probability(k)

    def __hash__(self):
        return hash((type(self), self.inner, self.drop_high, self.drop_low, self.total_rolls))


class SumDrop(Drop[T], Generic[T]):
    @classmethod
    def func(cls, parts):
        return sum(parts)

    def support_space(self) -> Optional[SupportSpace]:
        i_ss = self.inner.support_space()
        if i_ss is None:
            return None
        return SumSupportSpace((i_ss,) * self.actual_parts())


class ProdDrop(Drop[T], Generic[T]):
    @classmethod
    def func(cls, parts):
        return prod(parts)

    def support_space(self) -> Optional[SupportSpace]:
        i_ss = self.inner.support_space()
        if i_ss is None:
            return None
        return ProdSupportSpace((i_ss,) * self.actual_parts())


class DropBufferer(Bufferer, ABC):
    def __init__(self, inner: Bufferer, total_rolls: int, drop_low: int = 0, drop_high: int = 0):
        super().__init__()
        self.inner = inner
        self.total_rolls = total_rolls
        self.drop_low = drop_low
        self.drop_high = drop_high

    @classmethod
    @abstractmethod
    def func(cls, heap):
        pass

    def get_buffer(self, size) -> np.ndarray:
        heap = self.inner.get_buffer((size, self.total_rolls))
        if self.drop_low > 0:
            heap.partition(self.drop_low - 1, axis=1)
            heap = heap[:, self.drop_low:]
        if self.drop_high > 0:
            ind = len(heap) - self.drop_high
            heap.partition(ind, axis=1)
            heap = heap[:, :ind]
        return self.func(heap)


class DropSumBufferer(DropBufferer):
    @classmethod
    def func(cls, heap):
        return np.sum(heap, axis=1)


class DropProdBufferer(DropBufferer):
    @classmethod
    def func(cls, heap):
        return np.prod(heap, axis=1)


class BufferedSumDrop(BufferedDistribution[T], SumDrop[T], Generic[T]):
    def __init__(self, inner: BufferedDistribution[T], total_rolls: int, drop_low: int = 0, drop_high: int = 0):
        SumDrop.__init__(self, inner, total_rolls, drop_low, drop_high)
        BufferedDistribution.__init__(self, DropSumBufferer(inner.bufferer, total_rolls, drop_low, drop_high))


class BufferedProdDrop(BufferedDistribution[T], ProdDrop[T], Generic[T]):
    def __init__(self, inner: BufferedDistribution[T], total_rolls: int, drop_low: int = 0, drop_high: int = 0):
        ProdDrop.__init__(self, inner, total_rolls, drop_low, drop_high)
        BufferedDistribution.__init__(self, DropSumBufferer(inner.bufferer, total_rolls, drop_low, drop_high))


def drop_sum(inner: Distribution[T], total_rolls: int, drop_low: int = 0, drop_high: int = 0) -> Distribution[T]:
    if drop_low == 0 and drop_high == 0:
        return inner
    if (drop_low + drop_high) >= total_rolls:
        raise ValueError('cannot drop all rolls')
    if isinstance(inner, BufferedDistribution):
        return BufferedSumDrop(inner, total_rolls, drop_low, drop_high)
    return SumDrop(inner, total_rolls, drop_low, drop_high)


def drop_prod(inner: Distribution[T], total_rolls: int, drop_low: int = 0, drop_high: int = 0) -> Distribution[T]:
    if drop_low == 0 and drop_high == 0:
        return inner
    if (drop_low + drop_high) >= total_rolls:
        raise ValueError('cannot drop all rolls')
    if isinstance(inner, BufferedDistribution):
        return BufferedProdDrop(inner, total_rolls, drop_low, drop_high)
    return ProdDrop(inner, total_rolls, drop_low, drop_high)
