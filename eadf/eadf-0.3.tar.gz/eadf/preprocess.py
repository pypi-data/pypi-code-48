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
Preprocessing Methods
---------------------

This module hosts several preprocessing methods that can be used during
and before construction of an EADF object.
"""

from scipy.special import sph_harm
from scipy.interpolate import InterpolatedUnivariateSpline
import logging
import numpy as np


def setCompressionFactor(
    arrFourierData: np.ndarray,
    numAziInit: int,
    numCoEleInit: int,
    numFreqInit: int,
    isNarrowBand: int,
    numValue: float,
) -> tuple:
    """Calculate Subselection-Indices

    This method takes the supplied compression factor, which is
    not with respect to the number of Fourier coefficients to use
    but rather the amount of energy still present in them. this is
    achieved by analysing the spatial spectrum of the whole array in the
    following way:
    1. Flip the spectrum all into one quadrant
    2. normalize it with respect to the complete energy
    3. find all combinations of subsizes in azimuth and elevation
    such that the energy is lower than numValue
    4. find the pair of elevation and azimuth index such that it
    minimizes the execution time during sampling

    Parameters
    ----------
    numValue : float
        Factor to be set. Must be in (0,1].

    Returns
    -------
    float
        Returns the actual compression factor

    """

    # calculate the energy of the whole array
    # first get the norm of each spectrum, then sum along
    # pol, freq and elem
    numTotalEnergy = np.sqrt(np.sum(np.abs(arrFourierData) ** 2))

    # find the middle indices in the first two/three components
    middleAzi = int((numAziInit + (numAziInit % 2)) / 2)
    middleCoEle = int((numCoEleInit + (numCoEleInit % 2)) / 2)

    middlePadAzi = int(numAziInit % 2)
    middlePadCoEle = int(numCoEleInit % 2)

    # if the array is narrowband, we do not need to care about frequencies
    # in the pattern compression step
    if not isNarrowBand:
        middleFreq = int((numFreqInit + (numFreqInit % 2)) / 2)
        middlePadFreq = int(numFreqInit % 2)
        tplSum = (3, 4)
        lstCumSum = [0, 1, 2]
        tplMiddle = (middleCoEle, middleAzi, middleFreq)
        tplInit = (numCoEleInit, numAziInit, numFreqInit)
        tplPad = ((0, 0),)
    else:
        tplSum = (2, 3, 4)
        lstCumSum = [0, 1]
        tplMiddle = (middleCoEle, middleAzi)
        tplInit = (numCoEleInit, numAziInit)
        tplPad = ()

    # first we sum along polarisation and the array elements
    arrFoldedData = np.sum(np.abs(arrFourierData ** 2), axis=tplSum)

    # then we flip and add everything for each of the 2/3 dimensions
    arrFoldedData = arrFoldedData[:middleCoEle] + np.pad(
        arrFoldedData[middleCoEle:][::-1],
        ((0, middlePadCoEle), (0, 0)) + tplPad,
        mode="constant",
    )
    arrFoldedData = arrFoldedData[:, :middleAzi] + np.pad(
        arrFoldedData[:, middleAzi:][:, ::-1],
        ((0, 0), (0, middlePadAzi)) + tplPad,
        mode="constant",
    )
    if not isNarrowBand:
        arrFoldedData = arrFoldedData[:, :, :middleFreq] + np.pad(
            arrFoldedData[:, :, middleFreq:][:, :, ::-1],
            ((0, 0), (0, 0), (0, middlePadFreq)),
            mode="constant",
        )

    # get the partial norms for all the combinations
    arrCumulative = (
        np.sqrt(np.apply_over_axes(np.cumsum, arrFoldedData, lstCumSum))
        / numTotalEnergy
    )

    # find all subarrays such that they have less energy than required
    # the others will be the ones that we might select from
    arrInFeasibleSizes = arrCumulative <= numValue - 1e-12

    # # cost function is just the outer product of the three indexes, since
    # # we have to essentially do linear time operations when
    # # sampling
    if not isNarrowBand:
        arrCost = np.einsum(
            "i,j,k->ijk",
            np.linspace(1, middleCoEle, middleCoEle),
            np.linspace(1, middleAzi, middleAzi),
            np.linspace(1, middleFreq, middleFreq),
        )
    else:
        arrCost = np.einsum(
            "i,j->ij",
            np.linspace(1, middleCoEle, middleCoEle),
            np.linspace(1, middleAzi, middleAzi),
        )

    # all infeasible indices will be set to infinity, such that
    # they are not considered when finding the optimal cost indices
    arrCost[arrInFeasibleSizes] = np.inf

    # find the minimum in the 2D array of cost values
    minCostInd = np.unravel_index(np.argmin(arrCost, axis=None), arrCost.shape)

    # find the actual compression factor
    compressionFactor = arrCumulative[minCostInd]

    # now get the actual subselection arrays as booleans
    # here we have to apply the inverse fftshift
    # we have the +1, since minCostInd contains indices starting at
    # 0, but the linspace thingy is done from "1"
    arrIndCompress = (
        np.fft.ifftshift(
            np.abs(np.linspace(-tplMiddle[ii], +tplMiddle[ii], tplInit[ii]))
            <= mci + 1
        )
        for ii, mci in enumerate(minCostInd)
    )

    res = tuple([compressionFactor, *arrIndCompress])

    # return the compression factor we determined
    return res


def interpolateDataSphere(
    arrAziSample: np.ndarray,
    arrCoEleSample: np.ndarray,
    arrValues: np.ndarray,
    arrAziInter: np.ndarray,
    arrCoEleInter: np.ndarray,
    method="SH",
    **kwargs
) -> np.ndarray:
    """Interpolate Data located on a Sphere

    This method can be used for interpolating a function of the form
    f : S^2 -> C which is sampled on N arbitrary positions on the sphere.
    The input data is assumed to be in the format N x M1 x ... and the
    interpolation is broadcasted along M1 x ...
    The interpolation is always done using least squares, so for noisy data
    or overdetermined data with respect to the basis you should not encounter
    any problems.

    *Methods*
     - *SH* (Spherical Harmonics), see dissertation delGaldo,
       For these you have to supply *numN*
       as a kwarg, which determines the order of the SH basis. The number
       of total basis functions is then calculated via
       *numN x (numN + 1) + 1*. default=6


    Examples
    --------

    >>> # Interpolating a Stacked UCA using SH
    >>> import numpy as np
    >>> import matplotlib.pyplot as plt
    >>> import eadf
    >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
    >>> numSamples = 100
    >>> arrCoEleSm = np.random.uniform(0, np.pi, numSamples)
    >>> arrAziSm = np.random.uniform(0, 2 * np.pi, numSamples)
    >>> arrY = A.sample(arrAziSm, arrCoEleSm)
    >>> intCoEle = 40
    >>> intAzi = 80
    >>> arrAzi, arrCoEle = eadf.core.sampleAngles(intCoEle, intAzi)
    >>> grdAzi, grdCoEle = eadf.core.anglesToGrid(arrAzi, arrCoEle)
    >>> arrZ = eadf.core.interpolateDataSphere(
    >>>     arrAziSm,
    >>>     arrCoEleSm,
    >>>     arrY,
    >>>     grdAzi,
    >>>     grdCoEle,
    >>>     method='SH',
    >>>     numN=6
    >>> )
    >>> plt.subplot(211)
    >>> plt.imshow(np.real(arrZ[:, 0].reshape(intCoEle, intAzi)))
    >>> plt.subplot(212)
    >>> plt.imshow(np.real(
    >>>     A.sample(grdAzi, grdCoEle)[:, 0, 0, 0].reshape((intCoEle, intAzi))
    >>> ))
    >>> plt.show()

    Parameters
    ----------
    arrAziSample : np.ndarray
        Sampled Azimuth positions in radians
    arrCoEleSample : np.ndarray
        Sampled Co-Elevation positions in radians
    arrValues : np.ndarray
        Sampled values
    arrAziInter : np.ndarray
        Azimuth Positions we want the function to be evaluated in radians
    arrCoEleInter : np.ndarray
        CoElevation positions we want the function to be evaluated in radians
    method : type
        'SH' for spherical harmonics
    **kwargs : type
        Depends on method, see above

    Returns
    -------
    np.ndarray
        Description of returned object.

    """
    if (
        (arrAziSample.shape[0] != arrCoEleSample.shape[0])
        or (arrValues.shape[0] != arrAziSample.shape[0])
        or (arrValues.shape[0] != arrCoEleSample.shape[0])
    ):
        logging.error(
            (
                "interpolateDataSphere:"
                + "Input arrays of sizes %d azi, %d ele, %d values dont match"
            )
            % (
                arrAziSample.shape[0],
                arrCoEleSample.shape[0],
                arrValues.shape[0],
            )
        )
        return
    if arrAziInter.shape[0] != arrCoEleInter.shape[0]:
        logging.error(
            (
                "interpolateDataSphere:"
                + "Output arrays of sizes %d azi, %d ele dont match"
            )
            % (arrAziInter.shape[0], arrCoEleInter.shape[0])
        )
        return

    if method == "SH":
        kwargs.get("numN", 6)
        if kwargs["numN"] <= 0:
            logging.error(
                "interpolateDataSphere:"
                + "_genSHMatrix: numN must be greater than 0."
            )
            return
        else:
            return _interpolateSH(
                arrAziSample,
                arrCoEleSample,
                arrValues,
                arrAziInter,
                arrCoEleInter,
                kwargs["numN"],
            )
    else:
        logging.error("interpolateDataSphere: Method not implemented.")
        return


def _interpolateSH(
    arrAziSample: np.ndarray,
    arrCoEleSample: np.ndarray,
    arrValues: np.ndarray,
    arrAziInter: np.ndarray,
    arrCoEleInter: np.ndarray,
    numN: int,
) -> np.ndarray:
    """Interpolate function on Sphere using Spherical Harmonics

    See Dissertation of delGaldo for details.

    Parameters
    ----------
    arrAziSample : np.ndarray
        Sampled Azimuth positions in radians
    arrCoEleSample : np.ndarray
        Sampled Co-Elevation positions in radians
    arrValues : np.ndarray
        Sampled values
    arrAziInter : np.ndarray
        Azimuth Positions we want the function to be evaluated in radians
    arrCoEleInter : np.ndarray
        CoElevation positions we want the function to be evaluated in radians
    numN : int
        Order of the SH

    Returns
    -------
    np.ndarray
        Description of returned object.

    """

    # number of sampling points of the function
    numSamples = arrAziSample.shape[0]

    # matrix containing the basis functions evaluated at the
    # sampling positions. this one is used during the fitting of
    # the interpolation coefficients:
    # min || matSample * X - arrValues||_2^2
    matSample = _genSHMatrix(arrAziSample, arrCoEleSample, numN)

    # this matrix is used to generate the interpolated values, so it
    # contains the basis functions evaluated at the interpolation
    # points and we use the least squares fit to get the right linear
    # combinations
    matInter = _genSHMatrix(arrAziInter, arrCoEleInter, numN)

    # preserve the shape of the original data
    tplOrigShape = arrValues.shape

    # do the least squares fit
    arrLstSq = np.linalg.lstsq(
        matSample, arrValues.reshape((numSamples, -1)), rcond=-1
    )

    # extract the coefficients from the least squares fit
    arrCoeffs = arrLstSq[0]

    # calculate the interpolated values and return the same shape as
    # the input, but with different size in the interpolated first coordinate
    arrRes = matInter.dot(arrCoeffs).reshape((-1, *tplOrigShape[1:]))

    return arrRes


def _genSHMatrix(
    arrAzi: np.ndarray, arrCoEle: np.ndarray, numN: int
) -> np.ndarray:
    """Create a Matrix containing sampled Spherical harmonics

    Parameters
    ----------
    arrAzi : np.ndarray
        Azimuth angles to evaluate at in radians
    arrCoEle : np.ndarray
        CoElevation angles to evaluate at in radians
    numN : int
        Order of the SH basis > 0

    Returns
    -------
    np.ndarray
        Matrix containing sampled SH as its columns
    """

    # the spherical harmonics are always complex except in trivial
    # cases
    matR = np.zeros(
        (arrCoEle.shape[0], numN * (numN + 1) + 1), dtype="complex128"
    )

    # count the current basis element we are in
    numInd = 0

    # SH have two indices Y_LM with |L| <= M, see the scipy docu
    # on them
    for ii1 in range(numN + 1):
        for ii2 in range(ii1 + 1):
            # except for ii1 == 0, we always can generate two basis elements
            matR[:, numInd] = sph_harm(ii2, ii1, arrAzi, arrCoEle)
            if ii1 > 0:
                # note that matR[:, -numInd] = matR[:, numInd].conj()
                # would also work
                matR[:, -numInd] = sph_harm(-ii2, ii1, arrAzi, arrCoEle)
            numInd += 1
    return matR


def periodifyFreq(arrData: np.ndarray, paddingSize: int) -> np.ndarray:
    """Pad and Periodify the Pattern Data in Frequency Dimension

    This routine takes a sampled beampattern and extends it in frequency
    direction by the supplied size. Then it calculates two splines. One
    extrapolates to lower frequencies and the other one to higher ones.
    then they are overlayed in such a way that the last extrapolated data
    point fits to the first one, also in derivative. This ensures that
    an FFT in excitation frequency direction does not hurt interpolation
    performance that much.

    Parameters
    ----------
    arrData : np.ndarray
        data to pad
    paddingSize : int
        padding in frequency on one side
    Returns
    -------
    np.ndarray
        padded and extrapolated data
    """

    # pad the result in frequency direction
    arrRes = np.pad(
        arrData,
        ((0, 0), (0, 0), (0, paddingSize), (0, 0), (0, 0)),
        mode="constant",
    )

    # limit the number of values to the padding size and the data shape
    # this also corresponds to the degree of the polynomial used
    # and the number of derivatives that are correctly interpolated
    numVals = 3  # min(paddingSize, arrData.shape[2], 10)

    breakPoint = arrData.shape[2] * (
        2 * np.pi / (arrData.shape[2] + paddingSize)
    )

    print(breakPoint)

    # create the intervalls for the sampling and the extrapolation
    # here we have to keep in mind, that the data itself
    # contains no information about spacing and such
    tInner = np.linspace(0, breakPoint, arrData.shape[2], endpoint=False)

    # time values for the upper spline
    tUpper = np.linspace(breakPoint, 2 * np.pi, paddingSize, endpoint=False,)

    # time values for the lower spline
    tLower = np.linspace(
        breakPoint - 2 * np.pi, 0, paddingSize, endpoint=False
    )

    # mixing weights between the two splines.
    la = 0.5 * (np.cos(np.linspace(0, 1, paddingSize) * np.pi) + 1)

    for ii0 in range(arrData.shape[0]):
        print(ii0)
        for ii1 in range(arrData.shape[1]):
            for ii3 in range(arrData.shape[3]):
                for ii4 in range(arrData.shape[4]):
                    # extract the data
                    y = arrData[ii0, ii1, :, ii3, ii4]

                    # generate splines for the upper and lower ends
                    # and for each real and imaginary part seperately
                    splUpperR = InterpolatedUnivariateSpline(
                        tInner[-numVals:], np.real(y[-numVals:]), k=2
                    )
                    splUpperI = InterpolatedUnivariateSpline(
                        tInner[-numVals:], np.imag(y[-numVals:]), k=2
                    )
                    splLowerR = InterpolatedUnivariateSpline(
                        tInner[:numVals], np.real(y[:numVals]), k=2
                    )
                    splLowerI = InterpolatedUnivariateSpline(
                        tInner[:numVals], np.imag(y[:numVals]), k=2
                    )

                    # now we write the extrapolated values by mixing the
                    # two splines using la
                    arrRes[ii0, ii1, -paddingSize:, ii3, ii4] = (
                        la * splUpperR(tUpper) + (1 - la) * splLowerR(tLower)
                    ) + 1j * (
                        la * splUpperI(tUpper) + (1 - la) * splLowerI(tLower)
                    )
                    # arrRes[ii0, ii1, -paddingSize:, ii3, ii4]
                    #
                    # plt.subplot(211)
                    # plt.plot(tInner, np.real(y))
                    # plt.plot(tInner, np.imag(y))
                    #
                    # plt.plot(tUpper, splUpperR(tUpper))
                    # plt.plot(tUpper, splUpperI(tUpper))
                    # plt.plot(tLower, splLowerR(tLower))
                    # plt.plot(tLower, splLowerI(tLower))

                    # plt.plot(
                    #     np.block([tInner, tUpper]),
                    #     np.real(
                    #         arrRes[ii0, ii1, :, ii3, ii4]
                    #     )
                    # )
                    # plt.plot(
                    #     np.block([tInner, tUpper]),
                    #     np.imag(
                    #         arrRes[ii0, ii1, :, ii3, ii4]
                    #     )
                    # )
                    # plt.plot(
                    #     tLower,
                    #     np.real(
                    #         z1
                    #     )
                    # )
                    # plt.plot(
                    #     tLower,
                    #     np.imag(
                    #         z1
                    #     )
                    # )
                    #
                    # plt.subplot(212)
                    # arrRes[ii0, ii1, -paddingSize:, ii3, ii4] = z1
                    # plt.semilogy(np.abs(np.fft.fft(
                    #     arrRes[ii0, ii1, :, ii3, ii4], norm='ortho'
                    # )))
                    # arrRes[ii0, ii1, -paddingSize:, ii3, ii4] = z2
                    # plt.semilogy(np.abs(np.fft.fft(
                    #     arrRes[ii0, ii1, :, ii3, ii4], norm='ortho'
                    # )),linestyle=':')
                    # plt.semilogy(np.abs(np.fft.fft(
                    #     arrData[ii0, ii1, :, ii3, ii4], norm='ortho'
                    # )))
                    #
                    #
                    # plt.show()
    return arrRes
