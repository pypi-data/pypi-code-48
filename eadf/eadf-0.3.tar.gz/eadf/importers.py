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
Routines to import arrays
-------------------------

Basic Concepts
^^^^^^^^^^^^^^

Here we provide a collection of several importers to conveniently
create EADF objects from various data formats. For this purpose we
provide a set of so called *handshake formats*, which can be seen as
intermediate formats, which facilitate the construction of importers,
since for these hanshake formats we already provide tested conversion
routines to the internat data format.

Handshake Formats
^^^^^^^^^^^^^^^^^

For these formats there are readily available and tested importers. See
the respective importer methods for further details.

 - Regular (in space) Angular Data: 2*co-ele x azi x pol x freq x elem.
   This format is simply handled by the EADF class initialization. So, if your
   data is already in that format, just call EADF() with it.
 - Regular (in space) Spatial Fourier Data:
   2*co-ele-sptfreq x azi-sptfreq x pol x freq x elem
 - Angle List Data: Ang x Pol x Freq x Elem
"""

import numpy as np
import logging
from .eadf import EADF
from .preprocess import interpolateDataSphere
from .auxiliary import sampleAngles
from .auxiliary import toGrid


def fromAngleListData(
    arrAziData: np.ndarray,
    arrCoEleData: np.ndarray,
    arrAngleListData: np.ndarray,
    arrFreqData: np.ndarray,
    arrPos: np.ndarray,
    numAzi: int,
    numCoEle: int,
    numErrorTol=1e-4,
    method="SH",
) -> EADF:
    """Importer from the Angle List Data Handshake format

    This format allows to specify a list of angles (azi, ele)_i and
    beam pattern values v_i = (pol, freq, elem)_i which are then
    interpolated along the two angular domains to get a regular grid in
    azimuth and co-elevation. By default this is done using vector spherical
    harmonics, since they can deal with irregular sampling patterns
    quite nicely. In this format for each angular sampling point, we
    need to have excited the array elements with the same frequencies.

    Parameters
    ----------
    arrAziData : np.ndarray
        Sampled Azimuth Angles in radians
    arrCoEleData : np.ndarray
        Sampled Co-elevation Angles in radians
    arrAngleListData : np.ndarray
        List in  Angle x Freq x Pol x Element format
    arrFreqData : np.ndarray
        Frequencies the array was excited with in ascending order
    arrPos : np.ndarray
        Positions of the array elements
    numAzi : int
        number of regular azimuth samples used during interpolation > 0
    numCoEle : int
        number of regular elevation samples used during interpolation > 0
    numErrorTol : float
        error tolerance for coefficients fitting > 0
    method : string
        Interpolation Method, default='SH'

    Returns
    -------
    EADF
        Created Array

    """
    if (
        (arrAziData.shape[0] != arrCoEleData.shape[0])
        or (arrAngleListData.shape[0] != arrAziData.shape[0])
        or (arrAngleListData.shape[0] != arrCoEleData.shape[0])
    ):
        logging.error(
            (
                "fromAngleListData: Input arrays"
                + " of sizes %d azi, %d ele, %d values dont match"
            )
            % (
                arrAziData.shape[0],
                arrCoEleData.shape[0],
                arrAngleListData.shape[0],
            )
        )
        return
    if arrPos.shape[1] != arrAngleListData.shape[3]:
        logging.error(
            (
                "fromAngleListData:"
                + "Number of positions %d does not match provided data %d"
            )
            % (arrPos.shape[1], arrAngleListData.shape[3])
        )
        return
    if arrFreqData.shape[0] != arrAngleListData.shape[1]:
        logging.error(
            (
                "fromAngleListData:"
                + "Number of freqs %d does not match provided data %d"
            )
            % (arrFreqData.shape[0], arrAngleListData.shape[1])
        )
        return
    if numAzi < 0:
        logging.error("fromAngleListData: numAzi must be larger than 0.")
        return
    if numCoEle < 0:
        logging.error("fromAngleListData: numCoEle must be larger than 0.")
        return

    # we start with SH order of 5, see below
    # as soon as we offer more interpolation methods, we should handle
    # this differently
    numInterError = np.inf
    numN = 4

    # we steadily increase the approximation base size
    while numInterError > numErrorTol:
        numN += 1
        arrInter = interpolateDataSphere(
            arrAziData,
            arrCoEleData,
            arrAngleListData,
            arrAziData,
            arrCoEleData,
            numN=numN,
            method=method,
        )

        # calculate the current interpolation error
        numInterError = np.linalg.norm(
            arrInter - arrAngleListData
        ) / np.linalg.norm(arrAngleListData)

    # generate the regular grid, where we want to sample the array
    arrAzi, arrCoEle = sampleAngles(
        numAzi, numCoEle, lstEndPoints=[True, True]
    )
    grdAng, grdCoEle = toGrid(arrAzi, arrCoEle)

    # now run the interpolation for the regular grid, flip the pattern
    arrInter = interpolateDataSphere(
        arrAziData,
        arrCoEleData,
        arrAngleListData,
        grdAng,
        grdCoEle,
        numN=numN,
        method=method,
    ).reshape(
        numCoEle,
        numAzi,
        arrFreqData.shape[0],
        arrAngleListData.shape[1],
        arrPos.shape[1],
    )

    return EADF(arrInter, arrAzi, arrCoEle, arrFreqData, arrPos)
