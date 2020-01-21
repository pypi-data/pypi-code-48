
class Closure:
    CLOSED = 0
    MASS_CENTER = 1
    TWO_POINTS = 2
    ONE_POINT = 3
    RAYS = 4
    DIRECTION = 5

class ReduceMethod:
    KMT = 1
    REIDEMEISTER = 2
    EASY = 3


class TopolyException(Exception):
    pass

class PlotFormat:
    PNG = 'png'
    SVG = 'svg'
