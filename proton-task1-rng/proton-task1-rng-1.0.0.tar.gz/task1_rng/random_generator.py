import random
import warnings
import sys

class RandomGen(object):
    def __init__(self, random_nums = [-1, 0, 1, 2, 3],
                       probabilities = [0.01, 0.3, 0.58, 0.1, 0.01]):
        # Values that may be returned by next_num()
        self._random_nums = random_nums
        # Probability of the occurence of random_nums
        self._probabilities = probabilities

    def next_num(self):
        """
        Returns one of the randomNums. When this method
        is called multiple times over a long period,
        it should return the numbers roughly with the
        initialized probabilities.
        """
        # O(n) runtime, O(1) space.
        # Another possible solution is O(log(n)) runtime, O(n) space
        next_number = None
        rand_float = random.random()
        cumulative_probability = 0
        for number, prob in zip(self._random_nums, self._probabilities):
            cumulative_probability += prob
            if rand_float < cumulative_probability:
                next_number = number
                break
        return next_number
