#
#   Copyright EAVISE
#   Author: Tanguy Ophoff
#
#   Statistics on curves
#
import logging
import numpy as np
from scipy import interpolate, integrate

__all__ = ['auc', 'peak', 'point', 'threshold']
log = logging.getLogger(__name__)


def auc(curve, x=None, y=None):
    """ Computes the area under the curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X- and Y-values of the curve
        x (string): Name of the column that holds the X-axis values; Default **None**
        y (string): Name of the column that holds the Y-axis values; Default **None**

    Returns:
        Number: Area under the curve

    Note:
        If you do not give this function an X and/or Y column,
        it will default to using ``columns[0]`` as Y and ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.
    """
    if x is None:
        x = curve.columns[1]
    if y is None:
        y = curve.columns[0]

    if len(curve) == 0:
        return float('nan')

    if len(curve) == 1:
        curve = curve.loc[0]
        return curve[x] * curve[y]

    if not curve[x].is_monotonic_increasing:
        log.warning('Curve x-values are not sorted in increasing order. Sorting the values might not give correct results if there are multiple points with the same x value!')
        curve = curve.sort_values(x)

    x = curve[x].values
    y = curve[y].values

    # Add first and last point
    x = np.insert(x, 0, 0)
    y = np.insert(y, 0, y[0])
    x = np.append(x, x[-1])
    y = np.append(y, 0)

    return integrate.trapz(y, x)


def peak(curve, maximum=True, y=None):
    """ Find the min/max Y-value on a curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X-, Y-values of the curve
        maximum (boolean, optional): Whether to search for the maximum or minimum value; Default **True**
        y (string): Name of the column that holds the Y-axis values; Default **None**

    Returns:
        curve row: Point of the curve that contains the peak

    Note:
        If you do not give this function an Y column,
        it will default to using ``columns[0]`` as Y. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.
    """
    if y is None:
        y = curve.columns[0]

    # Get correct position on curve
    if maximum:
        pt = curve[y].idxmax()
    else:
        pt = curve[y].idxmin()

    return curve.loc[pt]


def point(curve, threshold, x=None):
    """ Return the point on the curve that matches the given detection threshold.

    Args:
        curve (pandas.DataFrame): dataframe containing the X-, Y- and confidence values of the curve
        threshold (number): detection confidence threshold to match
        x (string): Name of the column that holds the X-axis values; Default **None**

    Returns:
        curve row: Point of the curve that matches the detection confidence threshold

    Note:
        If you do not give this function an X column,
        it will default to using ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.

    Warning:
        If there are no detection confidence values higher than the given threshold, this function will return ``None``.
    """
    if x is None:
        x = curve.columns[1]

    # Sort curve by confidence
    if not curve['confidence'].is_monotonic_decreasing:
        curve = curve.sort_values('confidence', ascending=False)
    if not curve[x].is_monotonic_increasing:
        log.error('Curve x-values are not sorted in increasing order. This function works under the assumption that decreasing confidences, generate increasing X-values.')

    # Get last curve point where confidence >= threshold
    curve = curve[curve.confidence >= threshold]
    if curve.empty:
        return None
    return curve.loc[curve.index[-1]]


def threshold(curve, column, value, first=True, x=None):
    """ Compute the necessary detection threshold value to reach a certain value on the curve.

    Args:
        curve (pandas.DataFrame): dataframe containing the X-, Y- and confidence values of the curve
        column (string): on which axis to reach the threshold
        value (number): threshold value to reach on the curve
        first (boolean, optional): whether to reach the first or last value bigger than the given value; Default **True**
        x (string): name of the column that holds the X-axis values; Default **None**

    Returns:
        curve row: Point of the curve at which the threshold is reached

    Note:
        If you do not give this function an X column,
        it will default to using ``columns[1]`` as X. |br|
        The default curves in brambox (eg. PR, MRFPPI) do follow this convention.

    Warning:
        If the value is not reached on the curve, this function will return ``None``.
    """
    if x is None:
        x = curve.columns[1]

    # Sort curve by x axis
    if not curve['confidence'].is_monotonic_decreasing:
        curve = curve.sort_values('confidence', ascending=False)
    if not curve[x].is_monotonic_increasing:
        log.error('Curve x-values are not sorted in increasing order. This function works under the assumption that decreasing confidences, generate increasing X-values.')

    # Get correct position on curve
    threshold = curve[column] >= value
    if not threshold.any():
        return None

    if first:
        loc = curve[threshold].index[0]
    else:
        loc = curve[threshold].index[-1]

    return curve.loc[loc]
