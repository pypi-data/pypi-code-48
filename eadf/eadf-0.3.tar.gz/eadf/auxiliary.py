# Copyright 2019 S. Pawar, S. Semper
#     https://www.tu-ilmenau.de/it-ems/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
r"""
Auxiliary Methods
-----------------

These functions can be used in various places to make a lot of things
easier.
"""

import logging
import numpy as np


def cartesianToSpherical(arrA: np.ndarray) -> np.ndarray:
    """Convert from 3D to 3D Spherical Coordinates

    This function calculates 3D Spherical Coordinates from 3D cartesian
    coordinates, where we asume the points are aligned along the first
    axis=0.

    Parameters
    ----------
    arrA : np.ndarray
        N x 3 input array of N x X x Y x Z values. must not be complex.

    Returns
    -------
    np.ndarray
        N x 3 array of N x Azi (rad) x Co-Ele (rad) x Norm values .

    """

    if arrA.shape[1] != 3:
        logging.error("cartesianToSpherical: arrA has wrong second dimension.")
        return

    if arrA.dtype in ["complex64", "complex128"]:
        logging.error("cartesianToSpherical: arrA is complex.")
        return

    arrRes = np.empty((arrA.shape[0], 3), dtype="float")

    # Azimuth
    arrRes[:, 0] = np.arctan2(arrA[:, 1], arrA[:, 0])

    # Norm
    arrRes[:, 2] = np.linalg.norm(arrA, axis=1)

    # Co-Elevation
    arrRes[:, 1] = np.arccos(arrA[:, 2] / arrRes[:, 2])

    return arrRes


def columnwiseKron(arrA: np.ndarray, arrB: np.ndarray) -> np.ndarray:
    """Calculate column-wise Kronecker-Product

    Parameters
    ----------
    arrA : np.ndarray
        First input `arrA`.
    arrB : np.ndarray
        Second input `arrB`.

    Returns
    -------
    np.ndarray
        columnwisekron(arrA, arrB)

    """

    if arrA.shape[1] != arrB.shape[1]:
        logging.error("columnwiseKron: Matrices cannot be multiplied")
        return

    # the first matrix needs its rows repeated as many times as the
    # other one has rows. the second one needs to be placed repeated
    # as a whole so many times as the first one has rows.
    # the we just do an elementwise multiplication and are done.
    return np.multiply(
        np.repeat(arrA, arrB.shape[0], axis=0),
        np.tile(arrB, (arrA.shape[0], 1)),
    )


def sampleAngles(numAzi: int, numCoEle: int, **kwargs) -> tuple:
    """Generate regular samplings in azimuth and co-elevation

    By default we generate angles in azimuth and *co-elevation*. This is due
    to the fact that the EADF works best in this case. Both directions
    are sampled regularly.

    Parameters
    ----------
    numAzi : int
        Number of samples in azimuth direction. > 0
    numCoEle : int
        Number of samples in co-elevation direction. > 0
    lstEndPoints : [0, 0], optional
        If endpoints should be generated in the respective dimensions

    Returns
    -------
    tuple
        (anglesAzi, anglesCoEle) in radians

    """
    if numAzi < 1:
        logging.error("sampleAngles: numAzi is %d, must be > 0" % (numAzi))
        return
    if numCoEle < 1:
        logging.error("sampleAngles: numCoEle is %d, must be > 0" % (numCoEle))
        return

    lstEndPoints = kwargs.get("lstEndPoints", [False, False])

    if len(lstEndPoints) != 2:
        logging.error(
            "sampleAngles: lstEndPoints has length %d instead of 2."
            % (len(lstEndPoints))
        )
        return

    arrAzi = np.linspace(0, 2 * np.pi, numAzi, endpoint=lstEndPoints[0])
    arrCoEle = np.linspace(0, +np.pi, numCoEle, endpoint=lstEndPoints[1])
    return (arrAzi, arrCoEle)


def toGrid(*args) -> tuple:
    """Build up all pairwise combinations of angles

    For two given arrays of possibly unequal lengths N1 and N2 we generate
    two new arrays, that contain at the

    Parameters
    ----------
    *args :
        several array like structures that make up the
        coordinate axes' grid points.

    Returns
    -------
    tuple

    """

    grdTpl = np.meshgrid(*args)
    return (tt.flatten() for tt in grdTpl)
