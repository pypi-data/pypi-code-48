import random

import pytest

from permuta import PermSet, Perm
from permuta.permutils.symmetry import *


def get_inp():
    return [
        {'input': (Perm(()),), 'reverse': (Perm(()),), 'rotate': (Perm(()),), 'inverse': (Perm(()),)},
        {'input': (Perm((0,)),), 'reverse': (Perm((0,)),), 'rotate': (Perm((0,)),), 'inverse': (Perm((0,)),)},
        {'input': (Perm((0, 1)),), 'reverse': (Perm((1, 0)),), 'rotate': (Perm((1, 0)),), 'inverse': (Perm((0, 1)),)},
        {'input': (Perm((0, 1, 2, 3, 4, 5, 6, 7)),), 'reverse': (Perm((7, 6, 5, 4, 3, 2, 1, 0)),), 'rotate': (Perm((7, 6, 5, 4, 3, 2, 1, 0)),), 'inverse': (Perm((0, 1, 2, 3, 4, 5, 6, 7)),)},
        {'input': (Perm(()), Perm((0, 8, 6, 7, 2, 3, 1, 4, 5))), 'reverse': (Perm(()), Perm((5, 4, 1, 3, 2, 7, 6, 8, 0))), 'rotate': (Perm(()), Perm((8, 2, 4, 3, 1, 0, 6, 5, 7))), 'inverse': (Perm(()), Perm((0, 6, 4, 5, 7, 8, 2, 3, 1)))},
        {'input': (Perm((0,)), Perm((3, 0, 2, 1)), Perm((9, 6, 12, 8, 4, 7, 1, 11, 3, 5, 10, 2, 0))), 'reverse': (Perm((0,)), Perm((1, 2, 0, 3)), Perm((0, 2, 10, 5, 3, 11, 1, 7, 4, 8, 12, 6, 9))), 'rotate': (Perm((0,)), Perm((2, 0, 1, 3)), Perm((0, 6, 1, 4, 8, 3, 11, 7, 9, 12, 2, 5, 10))), 'inverse': (Perm((0,)), Perm((1, 3, 2, 0)), Perm((12, 6, 11, 8, 4, 9, 1, 5, 3, 0, 10, 7, 2)))},
        {'input': (Perm((1, 0)), Perm((0, 1, 6, 7, 2, 3, 5, 4, 8)), Perm((5, 2, 6, 3, 7, 13, 1, 11, 14, 10, 4, 12, 0, 8, 9))), 'reverse': (Perm((0, 1)), Perm((8, 4, 5, 3, 2, 7, 6, 1, 0)), Perm((9, 8, 0, 12, 4, 10, 14, 11, 1, 13, 7, 3, 6, 2, 5))), 'rotate': (Perm((0, 1)), Perm((8, 7, 4, 3, 1, 2, 6, 5, 0)), Perm((2, 8, 13, 11, 4, 14, 12, 10, 1, 0, 5, 7, 3, 9, 6))), 'inverse': (Perm((1, 0)), Perm((0, 1, 4, 5, 7, 6, 2, 3, 8)), Perm((12, 6, 1, 3, 10, 0, 2, 4, 13, 14, 9, 7, 11, 5, 8)))},
        {'input': (Perm((2, 3, 0, 1, 5, 4)), Perm((8, 6, 9, 4, 0, 5, 7, 2, 3, 1)), Perm((6, 2, 8, 1, 4, 7, 12, 9, 11, 10, 5, 0, 3))), 'reverse': (Perm((4, 5, 1, 0, 3, 2)), Perm((1, 3, 2, 7, 5, 0, 4, 9, 6, 8)), Perm((3, 0, 5, 10, 11, 9, 12, 7, 4, 1, 8, 2, 6))), 'rotate': (Perm((3, 2, 5, 4, 0, 1)), Perm((5, 0, 2, 1, 6, 4, 8, 3, 9, 7)), Perm((1, 9, 11, 0, 8, 2, 12, 7, 10, 5, 3, 4, 6))), 'inverse': (Perm((2, 3, 0, 1, 5, 4)), Perm((4, 9, 7, 8, 3, 5, 1, 6, 0, 2)), Perm((11, 3, 1, 12, 4, 10, 0, 5, 2, 7, 9, 8, 6)))},
        {'input': (Perm(()), Perm((0,)), Perm((0, 2, 1)), Perm((2, 3, 1, 0))), 'reverse': (Perm(()), Perm((0,)), Perm((1, 2, 0)), Perm((0, 1, 3, 2))), 'rotate': (Perm(()), Perm((0,)), Perm((2, 0, 1)), Perm((0, 1, 3, 2))), 'inverse': (Perm(()), Perm((0,)), Perm((0, 2, 1)), Perm((3, 2, 0, 1)))},
        {'input': (Perm(()), Perm((1, 0, 2)), Perm((0, 4, 1, 3, 2)), Perm((4, 12, 5, 7, 3, 10, 13, 9, 2, 6, 1, 8, 0, 11)), Perm((8, 11, 1, 0, 13, 7, 2, 4, 6, 5, 12, 9, 3, 10))), 'reverse': (Perm(()), Perm((2, 0, 1)), Perm((2, 3, 1, 4, 0)), Perm((11, 0, 8, 1, 6, 2, 9, 13, 10, 3, 7, 5, 12, 4)), Perm((10, 3, 9, 12, 5, 6, 4, 2, 7, 13, 0, 1, 11, 8))), 'rotate': (Perm(()), Perm((1, 2, 0)), Perm((4, 2, 0, 1, 3)), Perm((1, 3, 5, 9, 13, 11, 4, 10, 2, 6, 8, 0, 12, 7)), Perm((10, 11, 7, 1, 6, 4, 5, 8, 13, 2, 0, 12, 3, 9))), 'inverse': (Perm(()), Perm((1, 0, 2)), Perm((0, 2, 4, 3, 1)), Perm((12, 10, 8, 4, 0, 2, 9, 3, 11, 7, 5, 13, 1, 6)), Perm((3, 2, 6, 12, 7, 9, 8, 5, 0, 11, 13, 1, 10, 4)))},
        {'input': (Perm(()), Perm((1, 0)), Perm((2, 3, 4, 0, 1)), Perm((3, 1, 6, 4, 0, 5, 2)), Perm((6, 3, 4, 0, 1, 5, 2)), Perm((10, 1, 0, 2, 5, 9, 3, 6, 8, 7, 4)), Perm((9, 8, 0, 10, 7, 11, 3, 1, 2, 5, 4, 6))), 'reverse': (Perm(()), Perm((0, 1)), Perm((1, 0, 4, 3, 2)), Perm((2, 5, 0, 4, 6, 1, 3)), Perm((2, 5, 1, 0, 4, 3, 6)), Perm((4, 7, 8, 6, 3, 9, 5, 2, 0, 1, 10)), Perm((6, 4, 5, 2, 1, 3, 11, 7, 10, 0, 8, 9))), 'rotate': (Perm(()), Perm((0, 1)), Perm((1, 0, 4, 3, 2)), Perm((2, 5, 0, 6, 3, 1, 4)), Perm((3, 2, 0, 5, 4, 1, 6)), Perm((8, 9, 7, 4, 0, 6, 3, 1, 2, 5, 10)), Perm((9, 4, 3, 5, 1, 2, 0, 7, 10, 11, 8, 6))), 'inverse': (Perm(()), Perm((1, 0)), Perm((3, 4, 0, 1, 2)), Perm((4, 1, 6, 0, 3, 5, 2)), Perm((3, 4, 6, 1, 2, 5, 0)), Perm((2, 1, 3, 6, 10, 4, 7, 9, 8, 5, 0)), Perm((2, 7, 8, 6, 10, 9, 11, 4, 1, 0, 3, 5)))},
        {'input': (Perm((0,)), Perm((2, 0, 1)), Perm((1, 2, 7, 0, 4, 5, 3, 6)), Perm((4, 2, 3, 7, 10, 1, 0, 5, 8, 6, 9)), Perm((7, 3, 0, 2, 6, 9, 5, 10, 11, 4, 8, 1)), Perm((8, 10, 2, 1, 11, 9, 6, 0, 4, 7, 5, 3)), Perm((5, 2, 6, 0, 10, 11, 12, 3, 4, 8, 9, 7, 1))), 'reverse': (Perm((0,)), Perm((1, 0, 2)), Perm((6, 3, 5, 4, 0, 7, 2, 1)), Perm((9, 6, 8, 5, 0, 1, 10, 7, 3, 2, 4)), Perm((1, 8, 4, 11, 10, 5, 9, 6, 2, 0, 3, 7)), Perm((3, 5, 7, 4, 0, 6, 9, 11, 1, 2, 10, 8)), Perm((1, 7, 9, 8, 4, 3, 12, 11, 10, 0, 6, 2, 5))), 'rotate': (Perm((0,)), Perm((1, 0, 2)), Perm((4, 7, 6, 1, 3, 2, 0, 5)), Perm((4, 5, 9, 8, 10, 3, 1, 7, 2, 0, 6)), Perm((9, 0, 8, 10, 2, 5, 7, 11, 1, 6, 4, 3)), Perm((4, 8, 9, 0, 3, 1, 5, 2, 11, 6, 10, 7)), Perm((9, 0, 11, 5, 4, 12, 10, 1, 3, 2, 8, 7, 6))), 'inverse': (Perm((0,)), Perm((1, 2, 0)), Perm((3, 0, 1, 6, 4, 5, 7, 2)), Perm((6, 5, 1, 2, 0, 7, 9, 3, 8, 10, 4)), Perm((2, 11, 3, 1, 9, 6, 4, 0, 10, 5, 7, 8)), Perm((7, 3, 2, 11, 8, 10, 6, 9, 0, 5, 1, 4)), Perm((3, 12, 1, 7, 8, 0, 2, 11, 9, 10, 4, 5, 6)))},
        {'input': (Perm((0, 1, 3, 2)), Perm((5, 1, 3, 2, 6, 4, 0)), Perm((2, 7, 3, 6, 0, 1, 4, 5)), Perm((7, 0, 4, 5, 3, 2, 8, 1, 6, 9)), Perm((9, 8, 5, 11, 4, 1, 2, 0, 7, 6, 10, 3)), Perm((10, 4, 3, 2, 6, 0, 8, 5, 7, 1, 11, 9)), Perm((5, 0, 12, 2, 8, 10, 4, 7, 6, 11, 3, 1, 9))), 'reverse': (Perm((2, 3, 1, 0)), Perm((0, 4, 6, 2, 3, 1, 5)), Perm((5, 4, 1, 0, 6, 3, 7, 2)), Perm((9, 6, 1, 8, 2, 3, 5, 4, 0, 7)), Perm((3, 10, 6, 7, 0, 2, 1, 4, 11, 5, 8, 9)), Perm((9, 11, 1, 7, 5, 8, 0, 6, 2, 3, 4, 10)), Perm((9, 1, 3, 11, 6, 7, 4, 10, 8, 2, 12, 0, 5))), 'rotate': (Perm((3, 2, 0, 1)), Perm((0, 5, 3, 4, 1, 6, 2)), Perm((3, 2, 7, 5, 1, 0, 4, 6)), Perm((8, 2, 4, 5, 7, 6, 1, 9, 3, 0)), Perm((4, 6, 5, 0, 7, 9, 2, 3, 10, 11, 1, 8)), Perm((6, 2, 8, 9, 10, 4, 7, 3, 5, 0, 11, 1)), Perm((11, 1, 9, 2, 6, 12, 4, 5, 8, 0, 7, 3, 10))), 'inverse': (Perm((0, 1, 3, 2)), Perm((6, 1, 3, 2, 5, 0, 4)), Perm((4, 5, 0, 2, 6, 7, 3, 1)), Perm((1, 7, 5, 4, 2, 3, 8, 0, 6, 9)), Perm((7, 5, 6, 11, 4, 2, 9, 8, 1, 0, 10, 3)), Perm((5, 9, 3, 2, 1, 7, 4, 8, 6, 11, 0, 10)), Perm((1, 11, 3, 10, 6, 0, 8, 7, 4, 12, 5, 9, 2)))},
        {'input': (Perm(()), Perm((0, 2, 1)), Perm((1, 0, 2, 3)), Perm((1, 0, 4, 2, 3)), Perm((1, 2, 6, 4, 3, 5, 0)), Perm((3, 2, 4, 0, 5, 1, 8, 7, 10, 6, 9)), Perm((2, 7, 3, 12, 1, 10, 6, 8, 5, 11, 9, 4, 0)), Perm((10, 9, 4, 8, 11, 2, 12, 6, 5, 7, 0, 3, 1))), 'reverse': (Perm(()), Perm((1, 2, 0)), Perm((3, 2, 0, 1)), Perm((3, 2, 4, 0, 1)), Perm((0, 5, 3, 4, 6, 2, 1)), Perm((9, 6, 10, 7, 8, 1, 5, 0, 4, 2, 3)), Perm((0, 4, 9, 11, 5, 8, 6, 10, 1, 12, 3, 7, 2)), Perm((1, 3, 0, 7, 5, 6, 12, 2, 11, 8, 4, 9, 10))), 'rotate': (Perm(()), Perm((2, 0, 1)), Perm((2, 3, 1, 0)), Perm((3, 4, 1, 0, 2)), Perm((0, 6, 5, 2, 3, 1, 4)), Perm((7, 5, 9, 10, 8, 6, 1, 3, 4, 0, 2)), Perm((0, 8, 12, 10, 1, 4, 6, 11, 5, 2, 7, 3, 9)), Perm((2, 0, 7, 1, 10, 4, 5, 3, 9, 11, 12, 8, 6))), 'inverse': (Perm(()), Perm((0, 2, 1)), Perm((1, 0, 2, 3)), Perm((1, 0, 3, 4, 2)), Perm((6, 0, 1, 4, 3, 5, 2)), Perm((3, 5, 1, 0, 2, 4, 9, 7, 6, 10, 8)), Perm((12, 4, 0, 2, 11, 8, 6, 1, 7, 10, 5, 9, 3)), Perm((10, 12, 5, 11, 2, 8, 7, 9, 3, 1, 0, 4, 6)))},
        {'input': (Perm((0,)), Perm((1, 4, 2, 3, 0)), Perm((1, 6, 5, 0, 3, 4, 2)), Perm((5, 1, 0, 6, 4, 3, 2)), Perm((7, 0, 3, 6, 5, 4, 2, 1)), Perm((7, 0, 1, 5, 9, 4, 6, 11, 8, 12, 2, 3, 10)), Perm((4, 1, 5, 0, 10, 11, 9, 6, 8, 13, 12, 3, 2, 7)), Perm((12, 1, 3, 10, 13, 4, 9, 0, 11, 7, 2, 8, 6, 5, 14))), 'reverse': (Perm((0,)), Perm((0, 3, 2, 4, 1)), Perm((2, 4, 3, 0, 5, 6, 1)), Perm((2, 3, 4, 6, 0, 1, 5)), Perm((1, 2, 4, 5, 6, 3, 0, 7)), Perm((10, 3, 2, 12, 8, 11, 6, 4, 9, 5, 1, 0, 7)), Perm((7, 2, 3, 12, 13, 8, 6, 9, 11, 10, 0, 5, 1, 4)), Perm((14, 5, 6, 8, 2, 7, 11, 0, 9, 4, 13, 10, 3, 1, 12))), 'rotate': (Perm((0,)), Perm((0, 4, 2, 1, 3)), Perm((3, 6, 0, 2, 1, 4, 5)), Perm((4, 5, 0, 1, 2, 6, 3)), Perm((6, 0, 1, 5, 2, 3, 4, 7)), Perm((11, 10, 2, 1, 7, 9, 6, 12, 4, 8, 0, 5, 3)), Perm((10, 12, 1, 2, 13, 11, 6, 0, 5, 7, 9, 8, 3, 4)), Perm((7, 13, 4, 12, 9, 1, 2, 5, 3, 8, 11, 6, 14, 10, 0))), 'inverse': (Perm((0,)), Perm((4, 0, 2, 3, 1)), Perm((3, 0, 6, 4, 5, 2, 1)), Perm((2, 1, 6, 5, 4, 0, 3)), Perm((1, 7, 6, 2, 5, 4, 3, 0)), Perm((1, 2, 10, 11, 5, 3, 6, 0, 8, 4, 12, 7, 9)), Perm((3, 1, 12, 11, 0, 2, 7, 13, 8, 6, 4, 5, 10, 9)), Perm((7, 1, 10, 2, 5, 13, 12, 9, 11, 6, 3, 8, 0, 4, 14)))},
        {'input': (Perm(()), Perm((0, 1)), Perm((2, 3, 0, 1)), Perm((3, 0, 1, 2)), Perm((3, 2, 0, 1)), Perm((5, 7, 0, 8, 10, 2, 9, 1, 6, 3, 4)), Perm((7, 6, 9, 4, 1, 0, 10, 8, 5, 2, 3)), Perm((8, 0, 12, 9, 2, 7, 11, 1, 6, 5, 3, 10, 13, 4)), Perm((9, 10, 3, 14, 12, 7, 2, 6, 5, 0, 1, 13, 11, 8, 4))), 'reverse': (Perm(()), Perm((1, 0)), Perm((1, 0, 3, 2)), Perm((2, 1, 0, 3)), Perm((1, 0, 2, 3)), Perm((4, 3, 6, 1, 9, 2, 10, 8, 0, 7, 5)), Perm((3, 2, 5, 8, 10, 0, 1, 4, 9, 6, 7)), Perm((4, 13, 10, 3, 5, 6, 1, 11, 7, 2, 9, 12, 0, 8)), Perm((4, 8, 11, 13, 1, 0, 5, 6, 2, 7, 12, 14, 3, 10, 9))), 'rotate': (Perm(()), Perm((1, 0)), Perm((1, 0, 3, 2)), Perm((2, 1, 0, 3)), Perm((1, 0, 2, 3)), Perm((8, 3, 5, 1, 0, 10, 2, 9, 7, 4, 6)), Perm((5, 6, 1, 0, 7, 2, 9, 10, 3, 8, 4)), Perm((12, 6, 9, 3, 0, 4, 5, 8, 13, 10, 2, 7, 11, 1)), Perm((5, 4, 8, 12, 0, 6, 7, 9, 1, 14, 13, 2, 10, 3, 11))), 'inverse': (Perm(()), Perm((0, 1)), Perm((2, 3, 0, 1)), Perm((1, 2, 3, 0)), Perm((2, 3, 1, 0)), Perm((2, 7, 5, 9, 10, 0, 8, 1, 3, 6, 4)), Perm((5, 4, 9, 10, 3, 8, 1, 0, 7, 2, 6)), Perm((1, 7, 4, 10, 13, 9, 8, 5, 0, 3, 11, 6, 2, 12)), Perm((9, 10, 6, 2, 14, 8, 7, 5, 13, 0, 1, 12, 4, 11, 3)))},
        {'input': (Perm(()), Perm((0,)), Perm((2, 1, 3, 0, 4, 5)), Perm((2, 5, 4, 6, 1, 0, 3)), Perm((3, 4, 5, 6, 7, 2, 1, 0)), Perm((5, 4, 6, 8, 0, 9, 1, 7, 3, 2)), Perm((2, 8, 4, 5, 10, 0, 11, 3, 9, 6, 1, 7)), Perm((9, 11, 2, 4, 0, 8, 10, 12, 7, 6, 3, 1, 5)), Perm((1, 5, 11, 10, 12, 3, 2, 6, 7, 9, 4, 13, 0, 8))), 'reverse': (Perm(()), Perm((0,)), Perm((5, 4, 0, 3, 1, 2)), Perm((3, 0, 1, 6, 4, 5, 2)), Perm((0, 1, 2, 7, 6, 5, 4, 3)), Perm((2, 3, 7, 1, 9, 0, 8, 6, 4, 5)), Perm((7, 1, 6, 9, 3, 11, 0, 10, 5, 4, 8, 2)), Perm((5, 1, 3, 6, 7, 12, 10, 8, 0, 4, 2, 11, 9)), Perm((8, 0, 13, 4, 9, 7, 6, 2, 3, 12, 10, 11, 5, 1))), 'rotate': (Perm(()), Perm((0,)), Perm((2, 4, 5, 3, 1, 0)), Perm((1, 2, 6, 0, 4, 5, 3)), Perm((0, 1, 2, 7, 6, 5, 4, 3)), Perm((5, 3, 0, 1, 8, 9, 7, 2, 6, 4)), Perm((6, 1, 11, 4, 9, 8, 2, 0, 10, 3, 7, 5)), Perm((8, 1, 10, 2, 9, 0, 3, 4, 7, 12, 6, 11, 5)), Perm((1, 13, 7, 8, 3, 12, 6, 5, 0, 4, 10, 11, 9, 2))), 'inverse': (Perm(()), Perm((0,)), Perm((3, 1, 0, 2, 4, 5)), Perm((5, 4, 0, 6, 2, 1, 3)), Perm((7, 6, 5, 0, 1, 2, 3, 4)), Perm((4, 6, 9, 8, 1, 0, 2, 7, 3, 5)), Perm((5, 10, 0, 7, 2, 3, 9, 11, 1, 8, 4, 6)), Perm((4, 11, 2, 10, 3, 12, 9, 8, 5, 0, 6, 1, 7)), Perm((12, 0, 6, 5, 10, 1, 7, 8, 13, 9, 3, 2, 4, 11)))},
        {'input': (Perm((0, 1)), Perm((0, 1, 2)), Perm((1, 3, 2, 0)), Perm((6, 1, 3, 2, 0, 4, 5)), Perm((0, 6, 5, 3, 1, 4, 2, 7)), Perm((10, 6, 8, 0, 5, 3, 9, 1, 7, 4, 2)), Perm((6, 11, 2, 0, 3, 1, 12, 4, 7, 5, 10, 8, 9)), Perm((6, 12, 3, 9, 10, 4, 5, 11, 1, 13, 2, 0, 7, 8)), Perm((8, 3, 11, 2, 4, 5, 10, 13, 1, 9, 12, 7, 6, 0)), Perm((13, 7, 4, 3, 0, 12, 1, 10, 14, 5, 6, 11, 8, 9, 2))), 'reverse': (Perm((1, 0)), Perm((2, 1, 0)), Perm((0, 2, 3, 1)), Perm((5, 4, 0, 2, 3, 1, 6)), Perm((7, 2, 4, 1, 3, 5, 6, 0)), Perm((2, 4, 7, 1, 9, 3, 5, 0, 8, 6, 10)), Perm((9, 8, 10, 5, 7, 4, 12, 1, 3, 0, 2, 11, 6)), Perm((8, 7, 0, 2, 13, 1, 11, 5, 4, 10, 9, 3, 12, 6)), Perm((0, 6, 7, 12, 9, 1, 13, 10, 5, 4, 2, 11, 3, 8)), Perm((2, 9, 8, 11, 6, 5, 14, 10, 1, 12, 0, 3, 4, 7, 13))), 'rotate': (Perm((1, 0)), Perm((2, 1, 0)), Perm((0, 3, 1, 2)), Perm((2, 5, 3, 4, 1, 0, 6)), Perm((7, 3, 1, 4, 2, 5, 6, 0)), Perm((7, 3, 0, 5, 1, 6, 9, 2, 8, 4, 10)), Perm((9, 7, 10, 8, 5, 3, 12, 4, 1, 0, 2, 11, 6)), Perm((2, 5, 3, 11, 8, 7, 13, 1, 0, 10, 9, 6, 12, 4)), Perm((0, 5, 10, 12, 9, 8, 1, 2, 13, 4, 7, 11, 3, 6)), Perm((10, 8, 0, 11, 12, 5, 4, 13, 2, 1, 7, 3, 9, 14, 6))), 'inverse': (Perm((0, 1)), Perm((0, 1, 2)), Perm((3, 0, 2, 1)), Perm((4, 1, 3, 2, 5, 6, 0)), Perm((0, 4, 6, 3, 5, 2, 1, 7)), Perm((3, 7, 10, 5, 9, 4, 1, 8, 2, 6, 0)), Perm((3, 5, 2, 4, 7, 9, 0, 8, 11, 12, 10, 1, 6)), Perm((11, 8, 10, 2, 5, 6, 0, 12, 13, 3, 4, 7, 1, 9)), Perm((13, 8, 3, 1, 4, 5, 12, 11, 0, 9, 6, 2, 10, 7)), Perm((4, 6, 14, 3, 2, 9, 10, 1, 12, 13, 7, 11, 5, 0, 8)))},
        {'input': (Perm(()), Perm((0, 1)), Perm((1, 0)), Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((1, 3, 5, 2, 4, 0)), Perm((4, 3, 2, 5, 1, 0)), Perm((3, 1, 6, 0, 4, 2, 5)), Perm((6, 5, 2, 4, 0, 3, 7, 1)), Perm((1, 7, 10, 8, 0, 2, 9, 6, 4, 5, 3)), Perm((1, 12, 11, 7, 8, 10, 2, 3, 5, 4, 9, 0, 6))), 'reverse': (Perm(()), Perm((1, 0)), Perm((0, 1)), Perm((2, 1, 0)), Perm((1, 2, 0)), Perm((0, 4, 2, 5, 3, 1)), Perm((0, 1, 5, 2, 3, 4)), Perm((5, 2, 4, 0, 6, 1, 3)), Perm((1, 7, 3, 0, 4, 2, 5, 6)), Perm((3, 5, 4, 6, 9, 2, 0, 8, 10, 7, 1)), Perm((6, 0, 9, 4, 5, 3, 2, 10, 8, 7, 11, 12, 1))), 'rotate': (Perm(()), Perm((1, 0)), Perm((0, 1)), Perm((2, 1, 0)), Perm((2, 0, 1)), Perm((0, 5, 2, 4, 1, 3)), Perm((0, 1, 3, 4, 5, 2)), Perm((3, 5, 1, 6, 2, 0, 4)), Perm((3, 0, 5, 2, 4, 6, 7, 1)), Perm((6, 10, 5, 0, 2, 1, 3, 9, 7, 4, 8)), Perm((1, 12, 6, 5, 3, 4, 0, 9, 8, 2, 7, 10, 11))), 'inverse': (Perm(()), Perm((0, 1)), Perm((1, 0)), Perm((0, 1, 2)), Perm((0, 2, 1)), Perm((5, 0, 3, 1, 4, 2)), Perm((5, 4, 2, 1, 0, 3)), Perm((3, 1, 5, 0, 4, 6, 2)), Perm((4, 7, 2, 5, 3, 1, 0, 6)), Perm((4, 0, 5, 10, 8, 9, 7, 1, 3, 6, 2)), Perm((11, 0, 6, 7, 9, 8, 12, 3, 4, 10, 5, 2, 1)))},
        {'input': (Perm((0,)), Perm((0, 1)), Perm((1, 0)), Perm((0, 2, 1)), Perm((3, 2, 0, 1, 4)), Perm((4, 3, 5, 0, 2, 6, 1)), Perm((1, 0, 4, 7, 6, 5, 3, 2)), Perm((8, 0, 5, 2, 7, 3, 9, 4, 6, 1)), Perm((1, 2, 10, 7, 9, 8, 5, 11, 3, 4, 6, 0, 12, 13)), Perm((0, 11, 7, 8, 6, 14, 1, 2, 3, 12, 10, 4, 5, 9, 13)), Perm((8, 3, 10, 12, 5, 14, 7, 13, 2, 6, 11, 1, 9, 0, 4))), 'reverse': (Perm((0,)), Perm((1, 0)), Perm((0, 1)), Perm((1, 2, 0)), Perm((4, 1, 0, 2, 3)), Perm((1, 6, 2, 0, 5, 3, 4)), Perm((2, 3, 5, 6, 7, 4, 0, 1)), Perm((1, 6, 4, 9, 3, 7, 2, 5, 0, 8)), Perm((13, 12, 0, 6, 4, 3, 11, 5, 8, 9, 7, 10, 2, 1)), Perm((13, 9, 5, 4, 10, 12, 3, 2, 1, 14, 6, 8, 7, 11, 0)), Perm((4, 0, 9, 1, 11, 6, 2, 13, 7, 14, 5, 12, 10, 3, 8))), 'rotate': (Perm((0,)), Perm((1, 0)), Perm((0, 1)), Perm((2, 0, 1)), Perm((2, 1, 3, 4, 0)), Perm((3, 0, 2, 5, 6, 4, 1)), Perm((6, 7, 0, 1, 5, 2, 3, 4)), Perm((8, 0, 6, 4, 2, 7, 1, 5, 9, 3)), Perm((2, 13, 12, 5, 4, 7, 3, 10, 8, 9, 11, 6, 1, 0)), Perm((14, 8, 7, 6, 3, 2, 10, 12, 11, 1, 4, 13, 5, 0, 9)), Perm((1, 3, 6, 13, 0, 10, 5, 8, 14, 2, 12, 4, 11, 7, 9))), 'inverse': (Perm((0,)), Perm((0, 1)), Perm((1, 0)), Perm((0, 2, 1)), Perm((2, 3, 1, 0, 4)), Perm((3, 6, 4, 1, 0, 2, 5)), Perm((1, 0, 7, 6, 2, 5, 4, 3)), Perm((1, 9, 3, 5, 7, 2, 8, 4, 0, 6)), Perm((11, 0, 1, 8, 9, 6, 10, 3, 5, 4, 2, 7, 12, 13)), Perm((0, 6, 7, 8, 11, 12, 4, 2, 3, 13, 10, 1, 9, 14, 5)), Perm((13, 11, 8, 1, 14, 4, 9, 6, 0, 12, 2, 10, 3, 7, 5)))},
        {'input': (Perm(()), Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((1, 0, 3, 2)), Perm((7, 2, 3, 4, 1, 6, 0, 5)), Perm((0, 4, 8, 1, 7, 2, 9, 6, 3, 5)), Perm((7, 5, 9, 8, 1, 4, 3, 0, 2, 6)), Perm((3, 1, 10, 9, 6, 4, 2, 0, 5, 8, 7)), Perm((6, 4, 5, 10, 11, 0, 9, 7, 1, 2, 3, 8)), Perm((2, 7, 10, 8, 1, 4, 3, 5, 9, 11, 12, 6, 0)), Perm((8, 0, 5, 10, 3, 6, 11, 9, 4, 7, 1, 12, 2, 13)), Perm((0, 5, 10, 9, 12, 4, 14, 13, 8, 1, 6, 3, 7, 11, 2))), 'reverse': (Perm(()), Perm((2, 0, 1)), Perm((0, 1, 2)), Perm((2, 3, 0, 1)), Perm((5, 0, 6, 1, 4, 3, 2, 7)), Perm((5, 3, 6, 9, 2, 7, 1, 8, 4, 0)), Perm((6, 2, 0, 3, 4, 1, 8, 9, 5, 7)), Perm((7, 8, 5, 0, 2, 4, 6, 9, 10, 1, 3)), Perm((8, 3, 2, 1, 7, 9, 0, 11, 10, 5, 4, 6)), Perm((0, 6, 12, 11, 9, 5, 3, 4, 1, 8, 10, 7, 2)), Perm((13, 2, 12, 1, 7, 4, 9, 11, 6, 3, 10, 5, 0, 8)), Perm((2, 11, 7, 3, 6, 1, 8, 13, 14, 4, 12, 9, 10, 5, 0))), 'rotate': (Perm(()), Perm((1, 2, 0)), Perm((0, 1, 2)), Perm((2, 3, 0, 1)), Perm((1, 3, 6, 5, 4, 0, 2, 7)), Perm((9, 6, 4, 1, 8, 0, 2, 5, 7, 3)), Perm((2, 5, 1, 3, 4, 8, 0, 9, 6, 7)), Perm((3, 9, 4, 10, 5, 2, 6, 0, 1, 7, 8)), Perm((6, 3, 2, 1, 10, 9, 11, 4, 0, 5, 8, 7)), Perm((0, 8, 12, 6, 7, 5, 1, 11, 9, 4, 10, 3, 2)), Perm((12, 3, 1, 9, 5, 11, 8, 4, 13, 6, 10, 7, 2, 0)), Perm((14, 5, 0, 3, 9, 13, 4, 2, 6, 11, 12, 1, 10, 7, 8))), 'inverse': (Perm(()), Perm((1, 0, 2)), Perm((2, 1, 0)), Perm((1, 0, 3, 2)), Perm((6, 4, 1, 2, 3, 7, 5, 0)), Perm((0, 3, 5, 8, 1, 9, 7, 4, 2, 6)), Perm((7, 4, 8, 6, 5, 1, 9, 0, 3, 2)), Perm((7, 1, 6, 0, 5, 8, 4, 10, 9, 3, 2)), Perm((5, 8, 9, 10, 1, 2, 0, 7, 11, 6, 3, 4)), Perm((12, 4, 0, 6, 5, 7, 11, 1, 3, 8, 2, 9, 10)), Perm((1, 10, 12, 4, 8, 2, 5, 9, 0, 7, 3, 6, 11, 13)), Perm((0, 9, 14, 11, 5, 1, 10, 12, 8, 3, 2, 13, 4, 7, 6)))},
        {'input': (Perm(()), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((1, 2, 0)), Perm((0, 3, 2, 1, 4)), Perm((4, 2, 3, 1, 0)), Perm((1, 5, 0, 2, 3, 4)), Perm((2, 1, 4, 3, 0, 5)), Perm((7, 0, 1, 5, 6, 8, 4, 2, 3)), Perm((3, 0, 9, 5, 7, 2, 11, 6, 10, 12, 1, 4, 8)), Perm((5, 11, 0, 12, 2, 8, 10, 9, 7, 1, 3, 4, 6)), Perm((9, 12, 3, 1, 5, 6, 10, 11, 0, 7, 4, 8, 2)), Perm((9, 12, 3, 6, 8, 7, 10, 2, 11, 5, 4, 0, 1))), 'reverse': (Perm(()), Perm((1, 2, 0)), Perm((2, 0, 1)), Perm((0, 2, 1)), Perm((4, 1, 2, 3, 0)), Perm((0, 1, 3, 2, 4)), Perm((4, 3, 2, 0, 5, 1)), Perm((5, 0, 3, 4, 1, 2)), Perm((3, 2, 4, 8, 6, 5, 1, 0, 7)), Perm((8, 4, 1, 12, 10, 6, 11, 2, 7, 5, 9, 0, 3)), Perm((6, 4, 3, 1, 7, 9, 10, 8, 2, 12, 0, 11, 5)), Perm((2, 8, 4, 7, 0, 11, 10, 6, 5, 1, 3, 12, 9)), Perm((1, 0, 4, 5, 11, 2, 10, 7, 8, 6, 3, 12, 9))), 'rotate': (Perm(()), Perm((2, 0, 1)), Perm((1, 2, 0)), Perm((0, 2, 1)), Perm((4, 1, 2, 3, 0)), Perm((0, 1, 3, 2, 4)), Perm((3, 5, 2, 1, 0, 4)), Perm((1, 4, 5, 2, 3, 0)), Perm((7, 6, 1, 0, 2, 5, 4, 8, 3)), Perm((11, 2, 7, 12, 1, 9, 5, 8, 0, 10, 4, 6, 3)), Perm((10, 3, 8, 2, 1, 12, 0, 4, 7, 5, 6, 11, 9)), Perm((4, 9, 0, 10, 2, 8, 7, 3, 1, 12, 6, 5, 11)), Perm((1, 0, 5, 10, 2, 3, 9, 7, 8, 12, 6, 4, 11))), 'inverse': (Perm(()), Perm((0, 2, 1)), Perm((1, 0, 2)), Perm((2, 0, 1)), Perm((0, 3, 2, 1, 4)), Perm((4, 3, 1, 2, 0)), Perm((2, 0, 3, 4, 5, 1)), Perm((4, 1, 0, 3, 2, 5)), Perm((1, 2, 7, 8, 6, 3, 4, 0, 5)), Perm((1, 10, 5, 0, 11, 3, 7, 4, 12, 2, 8, 6, 9)), Perm((2, 9, 4, 10, 11, 0, 12, 8, 5, 7, 6, 1, 3)), Perm((8, 3, 12, 2, 10, 4, 5, 9, 11, 0, 6, 7, 1)), Perm((11, 12, 7, 2, 10, 9, 3, 5, 4, 0, 6, 8, 1)))},
        {'input': (Perm(()), Perm((0,)), Perm((1, 0)), Perm((3, 0, 2, 4, 1)), Perm((2, 5, 4, 3, 0, 6, 1)), Perm((6, 1, 3, 4, 2, 5, 0)), Perm((1, 6, 3, 2, 5, 4, 7, 0)), Perm((3, 4, 6, 7, 5, 2, 1, 0)), Perm((1, 2, 7, 4, 0, 5, 9, 8, 6, 3)), Perm((7, 0, 9, 3, 6, 8, 4, 1, 5, 2)), Perm((4, 9, 10, 3, 5, 1, 8, 2, 6, 7, 0)), Perm((6, 5, 3, 1, 9, 10, 8, 0, 4, 7, 2)), Perm((9, 5, 1, 8, 4, 0, 6, 10, 7, 2, 3)), Perm((3, 11, 5, 9, 8, 0, 2, 12, 4, 7, 1, 6, 10)), Perm((6, 12, 5, 14, 3, 13, 1, 8, 10, 2, 0, 11, 4, 7, 9))), 'reverse': (Perm(()), Perm((0,)), Perm((0, 1)), Perm((1, 4, 2, 0, 3)), Perm((1, 6, 0, 3, 4, 5, 2)), Perm((0, 5, 2, 4, 3, 1, 6)), Perm((0, 7, 4, 5, 2, 3, 6, 1)), Perm((0, 1, 2, 5, 7, 6, 4, 3)), Perm((3, 6, 8, 9, 5, 0, 4, 7, 2, 1)), Perm((2, 5, 1, 4, 8, 6, 3, 9, 0, 7)), Perm((0, 7, 6, 2, 8, 1, 5, 3, 10, 9, 4)), Perm((2, 7, 4, 0, 8, 10, 9, 1, 3, 5, 6)), Perm((3, 2, 7, 10, 6, 0, 4, 8, 1, 5, 9)), Perm((10, 6, 1, 7, 4, 12, 2, 0, 8, 9, 5, 11, 3)), Perm((9, 7, 4, 11, 0, 2, 10, 8, 1, 13, 3, 14, 5, 12, 6))), 'rotate': (Perm(()), Perm((0,)), Perm((0, 1)), Perm((3, 0, 2, 4, 1)), Perm((2, 0, 6, 3, 4, 5, 1)), Perm((0, 5, 2, 4, 3, 1, 6)), Perm((0, 7, 4, 5, 2, 3, 6, 1)), Perm((0, 1, 2, 7, 6, 3, 5, 4)), Perm((5, 9, 8, 0, 6, 4, 1, 7, 2, 3)), Perm((8, 2, 0, 6, 3, 1, 5, 9, 4, 7)), Perm((0, 5, 3, 7, 10, 6, 2, 1, 4, 9, 8)), Perm((3, 7, 0, 8, 2, 9, 10, 1, 4, 6, 5)), Perm((5, 8, 1, 0, 6, 9, 4, 2, 7, 10, 3)), Perm((7, 2, 6, 12, 4, 10, 1, 3, 8, 9, 0, 11, 5)), Perm((4, 8, 5, 10, 2, 12, 14, 1, 7, 0, 6, 3, 13, 9, 11))), 'inverse': (Perm(()), Perm((0,)), Perm((1, 0)), Perm((1, 4, 2, 0, 3)), Perm((4, 6, 0, 3, 2, 1, 5)), Perm((6, 1, 4, 2, 3, 5, 0)), Perm((7, 0, 3, 2, 5, 4, 1, 6)), Perm((7, 6, 5, 0, 1, 4, 2, 3)), Perm((4, 0, 1, 9, 3, 5, 8, 2, 7, 6)), Perm((1, 7, 9, 3, 6, 8, 4, 0, 5, 2)), Perm((10, 5, 7, 3, 0, 4, 8, 9, 6, 1, 2)), Perm((7, 3, 10, 2, 8, 1, 0, 9, 6, 4, 5)), Perm((5, 2, 9, 10, 4, 1, 6, 8, 3, 0, 7)), Perm((5, 10, 6, 0, 8, 2, 11, 9, 4, 3, 12, 1, 7)), Perm((10, 6, 9, 4, 12, 2, 0, 13, 7, 14, 8, 11, 1, 5, 3)))}
    ]


def test_rotate_set():
    inp = get_inp()
    for x in inp:
        assert rotate_set(x["input"]) == x["rotate"]


def test_inverse_set():
    inp = get_inp()
    for x in inp:
        assert inverse_set(x["input"]) == x["inverse"]


def test_reverse_set():
    inp = get_inp()
    for x in inp:
        assert reverse_set(x["input"]) == x["reverse"]


def test_roundtrip_rotate():
    for i in range(100):
        n = random.randint(0, 100)
        perm_set = PermSet(n)
        input_set = set([perm_set.random() for i in range(random.randint(1, 100))])
        output_set = input_set
        for i in range(4):
            output_set = rotate_set(output_set)

        assert input_set == output_set


def test_roundtrip_inverse():
    for i in range(100):
        n = random.randint(0, 100)
        perm_set = PermSet(n)
        input_set = set([perm_set.random() for i in range(random.randint(1, 100))])
        output_set = input_set
        for i in range(2):
            output_set = inverse_set(output_set)

        assert input_set == output_set


def test_roundtrip_reverse():
    for i in range(100):
        n = random.randint(0, 100)
        perm_set = PermSet(n)
        input_set = set([perm_set.random() for i in range(random.randint(1, 100))])
        output_set = input_set
        for i in range(4):
            output_set = reverse_set(output_set)

        assert input_set == output_set


def test_rotate_type():
    p = PermSet(10).random()
    assert type(rotate_set([p])) == list
    assert type(rotate_set((p,))) == tuple
    assert type(rotate_set({p})) == set

def test_rotate_set_length():
    perm_list = [PermSet(6).random() for i in range(10)]
    perm_tup = tuple(perm_list)
    perm_set = set(perm_list)

    assert len(rotate_set(perm_list)) == len(perm_list)
    assert len(rotate_set(perm_tup)) == len(perm_tup)
    assert len(rotate_set(perm_set)) == len(perm_set)


def test_inverse_type():
    p = PermSet(10).random()
    assert type(inverse_set([p])) == list
    assert type(inverse_set((p,))) == tuple
    assert type(inverse_set({p})) == set

def test_inverse_set_length():
    perm_list = [PermSet(6).random() for i in range(10)]
    perm_tup = tuple(perm_list)
    perm_set = set(perm_list)

    assert len(inverse_set(perm_list)) == len(perm_list)
    assert len(inverse_set(perm_tup)) == len(perm_tup)
    assert len(inverse_set(perm_set)) == len(perm_set)

def test_reverse_type():
    p = PermSet(10).random()
    assert type(reverse_set([p])) == list
    assert type(reverse_set((p,))) == tuple
    assert type(reverse_set({p})) == set

def test_reverse_set_length():
    perm_list = [PermSet(6).random() for i in range(10)]
    perm_tup = tuple(perm_list)
    perm_set = set(perm_list)

    assert len(reverse_set(perm_list)) == len(perm_list)
    assert len(reverse_set(perm_tup)) == len(perm_tup)
    assert len(reverse_set(perm_set)) == len(perm_set)


def test_raise_TypeError():
    inp = (2,
           2.04,
           1.0,
           0,
           True,
           None,
           "Hello World",
           [""],
           [Perm((1, 0, 3, 2)), 0],
           [Perm((1, 0, 3, 2)), "Hello"],
           [Perm((1, 0, 3, 2)), 0.4],
           [Perm((1, 0, 3, 2)), False],
           {Perm((1, 0, 3, 2)), 0},
           (Perm((1, 0, 3, 2)), 0))
    for i in inp:
        with pytest.raises(TypeError):
            rotate_set(i)
        with pytest.raises(TypeError):
            inverse_set(i)
        with pytest.raises(TypeError):
            reverse_set(i)


def test_input_all_symmetries():
    inp = [
        {(Perm(()),)},
        {(Perm((0,)),)},
        {(Perm((0, 1)),), (Perm((1, 0)),)},
        {(Perm((0, 1, 2)),), (Perm((2, 1, 0)),)},
        {(Perm((0, 1, 2, 3)),), (Perm((3, 2, 1, 0)),)},
        {(Perm((0, 1, 2, 3, 4)),), (Perm((4, 3, 2, 1, 0)),)},
        {(Perm((0, 1, 2, 3, 4, 5)),), (Perm((5, 4, 3, 2, 1, 0)),)},
        {(Perm((0, 2, 1)),), (Perm((1, 2, 0)),), (Perm((1, 0, 2)),), (Perm((2, 0, 1)),)},
        {
            (Perm((0, 2, 3, 1)),), (Perm((2, 1, 3, 0)),), (Perm((2, 0, 1, 3)),), (Perm((3, 0, 2, 1)),),
            (Perm((1, 3, 2, 0)),), (Perm((0, 3, 1, 2)),), (Perm((3, 1, 0, 2)),), (Perm((1, 2, 0, 3)),)
        },
        {
            (Perm((0, 3, 1, 2)), Perm((2, 1, 3, 0))), (Perm((0, 2, 3, 1)), Perm((3, 1, 0, 2))),
            (Perm((1, 3, 2, 0)), Perm((2, 0, 1, 3))), (Perm((1, 2, 0, 3)), Perm((3, 0, 2, 1)))
        },
        {
            (Perm((0, 2, 3, 1)), Perm((1, 3, 0, 2))), (Perm((1, 3, 0, 2)), Perm((2, 1, 3, 0))),
            (Perm((1, 3, 0, 2)), Perm((2, 0, 1, 3))), (Perm((1, 3, 0, 2)), Perm((3, 0, 2, 1))),
            (Perm((1, 3, 2, 0)), Perm((2, 0, 3, 1))), (Perm((0, 3, 1, 2)), Perm((2, 0, 3, 1))),
            (Perm((2, 0, 3, 1)), Perm((3, 1, 0, 2))), (Perm((1, 2, 0, 3)), Perm((2, 0, 3, 1)))
        }
    ]

    for x in inp:
        for i in x:
            assert all_symmetry_sets(i) == x

def test_length_of_output_should_be_1_2_4_or_8():
    for i in range(100):
        n = random.randint(0, 100)
        perm_set = PermSet(n)
        input_set = set([perm_set.random() for i in range(random.randint(1, 100))])

        assert len(all_symmetry_sets(input_set)) in [1, 2, 4, 8]


def test_all_symmetries_raise_TypeError():
    inp = (2,
           2.04,
           1.0,
           0,
           True,
           None,
           "Hello World",
           [""],
           [Perm((1, 0, 3, 2)), 0],
           [Perm((1, 0, 3, 2)), "Hello"],
           [Perm((1, 0, 3, 2)), 0.4],
           [Perm((1, 0, 3, 2)), False],
           {Perm((1, 0, 3, 2)), 0},
           (Perm((1, 0, 3, 2)), 0))
    for i in inp:
        with pytest.raises(TypeError):
            all_symmetry_sets(i)

def test_input_lex_min():
    inp = [
        {"input": {(Perm(()),)}, "output": (Perm(()),)},
        {"input": {(Perm((0, 1)),), (Perm((1, 0)),)}, "output": (Perm((0, 1)),)},
        {"input": {(Perm((0, 1, 2)),), (Perm((2, 1, 0)),)}, "output": (Perm((0, 1, 2)),)},
        {"input": {(Perm((0, 1, 2, 3)),), (Perm((3, 2, 1, 0)),)}, "output": (Perm((0, 1, 2, 3)),)},
        {"input": {(Perm((0, 1, 2, 3, 4)),), (Perm((4, 3, 2, 1, 0)),)}, "output": (Perm((0, 1, 2, 3, 4)),)},
        {"input": {(Perm((0, 1, 2, 3, 4, 5)),), (Perm((5, 4, 3, 2, 1, 0)),)}, "output": (Perm((0, 1, 2, 3, 4, 5)),)},
        {"input": {(Perm((0, 2, 1)),), (Perm((1, 2, 0)),), (Perm((1, 0, 2)),), (Perm((2, 0, 1)),)}, "output": (Perm((0, 2, 1)),)},
        {
            "input":
                {
                    (Perm((0, 2, 3, 1)),), (Perm((2, 1, 3, 0)),), (Perm((2, 0, 1, 3)),), (Perm((3, 0, 2, 1)),),
                    (Perm((1, 3, 2, 0)),), (Perm((0, 3, 1, 2)),), (Perm((3, 1, 0, 2)),), (Perm((1, 2, 0, 3)),)
                },
            "output": (Perm((0, 2, 3, 1)),)
        },
        {
            "input":
                {
                    (Perm((0, 3, 1, 2)), Perm((2, 1, 3, 0))), (Perm((0, 2, 3, 1)), Perm((3, 1, 0, 2))),
                    (Perm((1, 3, 2, 0)), Perm((2, 0, 1, 3))), (Perm((1, 2, 0, 3)), Perm((3, 0, 2, 1)))
                },
            "output": (Perm((0, 2, 3, 1)), Perm((3, 1, 0, 2)))
        },
        {
            "input":
                {
                    (Perm((0, 2, 3, 1)), Perm((1, 3, 0, 2))), (Perm((1, 3, 0, 2)), Perm((2, 1, 3, 0))),
                    (Perm((1, 3, 0, 2)), Perm((2, 0, 1, 3))), (Perm((1, 3, 0, 2)), Perm((3, 0, 2, 1))),
                    (Perm((1, 3, 2, 0)), Perm((2, 0, 3, 1))), (Perm((0, 3, 1, 2)), Perm((2, 0, 3, 1))),
                    (Perm((2, 0, 3, 1)), Perm((3, 1, 0, 2))), (Perm((1, 2, 0, 3)), Perm((2, 0, 3, 1)))
                },
            "output": (Perm((0, 2, 3, 1)), Perm((1, 3, 0, 2)))
        }
    ]

    for x in inp:
        for i in x["input"]:
            assert lex_min(i) == x["output"]


def test_lex_min_raise_TypeError():
    inp = (2,
           2.04,
           1.0,
           0,
           True,
           None,
           "Hello World",
           [""],
           [Perm((1, 0, 3, 2)), 0],
           [Perm((1, 0, 3, 2)), "Hello"],
           [Perm((1, 0, 3, 2)), 0.4],
           [Perm((1, 0, 3, 2)), False],
           {Perm((1, 0, 3, 2)), 0},
           (Perm((1, 0, 3, 2)), 0))
    for i in inp:
        with pytest.raises(TypeError):
            lex_min(i)