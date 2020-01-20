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
Mathematical Core Routines
--------------------------

In this submodule we place all the mathematical and general core routines
which are used throughout the package. These are not intended for
direct use, but are still documented in order to allow new developers who
are unfamiliar with the code base to get used to the internal structure.
"""

import logging
import numpy as np


def fourierToSampled(arrData: np.ndarray, axes: tuple) -> tuple:
    """Transform the Regularly Sampled Fourier Data in Spatial Domain

    We assume that the provided data was discretely Fourier transformed in both
    angular directions, so we have Fourier samples on a regular 2D grid.
    Moreover in this format all spatial freqencies are obtained for all
    the same wave-freqency samples. This routines then gives back the
    beampattern on a regular angular grid together with the right
    angular frequency bins.

    Parameters
    ----------
    arrData : np.ndarray
        Fourier data in the form
        2 * co-ele x azi x freq x pol x elem

    Returns
    -------
    tuple
        Inverse Fourier Transform and the respective sample frequencies

    """
    if len(arrData.shape) != 5:
        logging.error(
            "fourierToSampled: arrData has wrong number of dimensions"
        )
        return
    if arrData.shape[3] > 2:
        logging.error(
            "fourierToSampled: There must be at most 2 polarisations"
        )
        return

    freqs = tuple(
        (arrData.shape[ii] * np.fft.fftfreq(arrData.shape[ii])) for ii in axes
    )

    scaling = 1.0
    for aa in axes:
        scaling *= arrData.shape[aa]

    # the frequencies are generated according to (5) in the EADF paper
    res = np.fft.ifftn(arrData, axes=axes) * scaling

    return (res, *freqs)


def sampledToFourier(arrData: np.ndarray, axes: tuple) -> tuple:
    """Transform the regularly sampled data in frequency domain

    Here we assume that the data is already flipped along co-elevation,
    rotated along azimuth as described in the EADF paper and in the wideband
    case it is also preiodified in excitation frequency direction such that we
    can just calculate the respective 2D/3D FFT from this along the first two
    /three axes.

    Parameters
    ----------
    data : np.ndarray
        Raw sampled and preprocessed data in the form
        2 * co-ele x azi x freq x pol x elem

    Returns
    -------
    (np.ndarray, np.ndarray, np.ndarray)
        Fourier Transform and the respective sample frequencies

    """
    if (arrData.shape[0] % 2) != 0:
        logging.error(
            "sampledToFourier: 1st dim of arrData must have even size."
        )
        return
    if len(arrData.shape) != 5:
        logging.error(
            "sampledToFourier: arrData has wrong number of dimensions"
        )
        return
    if arrData.shape[3] > 2:
        logging.error(
            "sampledToFourier: There must be at most 2 polarisations"
        )
        return

    freqs = tuple(
        (arrData.shape[ii] * np.fft.fftfreq(arrData.shape[ii])) for ii in axes
    )

    scaling = 1.0
    for aa in axes:
        scaling *= arrData.shape[aa]

    # the frequencies are generated according to (5) in the EADF paper
    res = np.fft.fftn(arrData, axes=axes) / scaling

    return (res, *freqs)


def _inversePatternTransformNarrowBand(
    arrAzi: np.ndarray, arrCoEle: np.ndarray, arrData: np.ndarray, xp,
) -> np.ndarray:
    """Samples the Pattern by using the Fourier Coefficients

    This function does the heavy lifting in the EADF evaluation process.
    It is used to sample the beampattern and the derivative itself, by
    evaluating d_phi * Gamma * d_theta^t as stated in (6) in the EADF
    paper by Landmann and delGaldo. It broadcasts this product over
    the last three coordinates of the fourier data, so across all
    polarisations, wave frequency bins and array elements.

    By changing d_phi (arrAzi) and d_theta(arRele) acordingly in the arguments
    one can calculate either the derivative or the pattern itself.

    Parameters
    ----------
    arrAzi : np.ndarray
        array of fourier kernels in azimuth direction
    arrCoEle : np.ndarray
        array of fourier kernels in co-elevation direction
    arrData : np.ndarray
        the Fourier coefficients to use

    Returns
    -------
    np.ndarray
        beam pattern values at arrAzi, arrCoEle
    """
    # equation (6) in EADF paper by landmann and del galdo
    return xp.einsum(
        "ijl...,ik,jk->k...", arrData, arrCoEle, arrAzi, optimize="optimal",
    )


def _inversePatternTransform(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    arrFreq: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Samples the Pattern by using the Fourier Coefficients

    This function does the heavy lifting in the EADF evaluation process.
    It is used to sample the beampattern and the derivative itself, by
    evaluating d_phi * Gamma * d_theta^t as stated in (6) in the EADF
    paper by Landmann and delGaldo. It broadcasts this product over
    the last three coordinates of the fourier data, so across all
    polarisations, wave frequency bins and array elements.

    By changing d_phi (arrAzi) and d_theta(arRele) acordingly in the arguments
    one can calculate either the derivative or the pattern itself.

    Parameters
    ----------
    arrAzi : np.ndarray
        array of fourier kernels in azimuth direction
    arrCoEle : np.ndarray
        array of fourier kernels in co-elevation direction
    arrFreq : np.ndarray
        array of fourier kernels in co-elevation direction
    arrData : np.ndarray
        the Fourier coefficients to use

    Returns
    -------
    np.ndarray
        beam pattern values at arrAzi, arrCoEle
    """

    # equation (6) in EADF paper by landmann and del galdo
    # extended to another frequency dimension
    return xp.einsum(
        "ijl...,ik,jk,lk->k...",
        arrData,
        arrCoEle,
        arrAzi,
        arrFreq,
        optimize="optimal",
    )


def evaluatePatternNarrowBand(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    muAzi: np.ndarray,
    muCoEle: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Sample the Beampattern at Dedicated Angles

    Parameters
    ----------
    arrAzi : np.ndarray
        azimuth angles to sample at in radians
    arrCoEle : np.ndarray
        co-elevation angles to sample at in radians
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muCoEle : np.ndarray
        spatial frequency bins in co-elevation direction
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
    np.ndarray
        sampled values
    """
    # equation (7) in the EADF Paper
    arrMultAzi = xp.exp(1j * xp.outer(muAzi, arrAzi))
    arrMultCoEle = xp.exp(1j * xp.outer(muCoEle, arrCoEle))

    return _inversePatternTransformNarrowBand(
        arrMultAzi, arrMultCoEle, arrData, xp
    )


def evaluatePattern(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    arrFreq: np.ndarray,
    muAzi: np.ndarray,
    muCoEle: np.ndarray,
    muFreq: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Sample the Beampattern at Dedicated Angles

    Parameters
    ----------
    arrAzi : np.ndarray
        azimuth angles to sample at in radians
    arrCoEle : np.ndarray
        co-elevation angles to sample at in radians
    arrFreq : np.ndarray
        frequencies to sample at in Hertz
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muCoEle : np.ndarray
        spatial frequency bins in co-elevation direction
    muFreq : np.ndarray
        spatial frequency bins in excitation frequency direction
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
    np.ndarray
        sampled values
    """
    # equation (7) in the EADF Paper
    arrMultAzi = xp.exp(1j * xp.outer(muAzi, arrAzi))
    arrMultCoEle = xp.exp(1j * xp.outer(muCoEle, arrCoEle))

    # extension in frequency domain
    arrMultFreq = xp.exp(1j * xp.outer(muFreq, arrFreq))

    return _inversePatternTransform(
        arrMultAzi, arrMultCoEle, arrMultFreq, arrData, xp
    )


def evaluateGradientNarrowBand(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    muAzi: np.ndarray,
    muCoEle: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Sample the Beampattern Gradients at Dedicated Angles

    Parameters
    ----------
    arrAzi : np.ndarray
        azimuth angles to sample at in radians
    arrCoEle : np.ndarray
        co-elevation angles to sample at in radians
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muCoEle : np.ndarray
        spatial frequency bins in co-elevation direction
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
        np.ndarray
    """
    # equation (7) in the EADF Paper
    arrMultAzi = xp.exp(1j * xp.outer(muAzi, arrAzi))
    arrMultCoEle = xp.exp(1j * xp.outer(muCoEle, arrCoEle))

    # equation (8) in the EADF Paper
    arrMultAziDeriv = xp.multiply(1j * muAzi, arrMultAzi.T).T
    arrMultCoEleDeriv = xp.multiply(1j * muCoEle, arrMultCoEle.T).T

    # build up array of gradient by calling the pattern transform
    # twice and then stacking them along a new last dimension
    return xp.stack(
        (
            _inversePatternTransformNarrowBand(
                arrMultAziDeriv, arrMultCoEle, arrData, xp
            ),
            _inversePatternTransformNarrowBand(
                arrMultAzi, arrMultCoEleDeriv, arrData, xp
            ),
        ),
        axis=-1,
    )


def evaluateGradient(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    arrFreq: np.ndarray,
    muAzi: np.ndarray,
    muCoEle: np.ndarray,
    muFreq: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Sample the Beampattern Gradients at Dedicated Angles

    Parameters
    ----------
    arrAzi : np.ndarray
        azimuth angles to sample at in radians
    arrCoEle : np.ndarray
        co-elevation angles to sample at in radians
    arrFreq : np.ndarray
        frequencies to sample at in Hertz
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muCoEle : np.ndarray
        spatial frequency bins in co-elevation direction
    muFreq : np.ndarray
        spatial frequency bins in excitation frequency direction
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
        np.ndarray
    """
    # equation (7) in the EADF Paper
    arrMultAzi = xp.exp(1j * xp.outer(muAzi, arrAzi))
    arrMultCoEle = xp.exp(1j * xp.outer(muCoEle, arrCoEle))

    # extension in frequency domain
    arrMultFreq = xp.exp(1j * xp.outer(muFreq, arrFreq))

    # equation (8) in the EADF Paper
    arrMultAziDeriv = xp.multiply(1j * muAzi, arrMultAzi.T).T
    arrMultCoEleDeriv = xp.multiply(1j * muCoEle, arrMultCoEle.T).T

    # extension in frequency domain
    arrMultFreqDeriv = xp.multiply(1j * muFreq, arrMultFreq.T).T

    # build up array of gradient by calling the pattern transform
    # twice and then stacking them along a new last dimension
    return xp.stack(
        (
            _inversePatternTransform(
                arrMultAziDeriv, arrMultCoEle, arrMultFreq, arrData, xp
            ),
            _inversePatternTransform(
                arrMultAzi, arrMultCoEleDeriv, arrMultFreq, arrData, xp
            ),
            _inversePatternTransform(
                arrMultAzi, arrMultCoEleDeriv, arrMultFreqDeriv, arrData, xp
            ),
        ),
        axis=-1,
    )


def evaluateHessianNarrowBand(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    muAzi: np.ndarray,
    muCoEle: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Sample the Beampattern Gradients at Dedicated Angles

    Parameters
    ----------
    arrAzi : np.ndarray
        azimuth angles to sample at in radians
    arrCoEle : np.ndarray
        co-elevation angles to sample at in radians
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muCoEle : np.ndarray
        spatial frequency bins in co-elevation direction
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
        np.ndarray
    """
    # equation (7) in the EADF Paper
    arrMultAzi = xp.exp(1j * xp.outer(muAzi, arrAzi))
    arrMultCoEle = xp.exp(1j * xp.outer(muCoEle, arrCoEle))

    # equation (8) in the EADF Paper
    arrMultAziDeriv = xp.multiply(1j * muAzi, arrMultAzi.T).T
    arrMultCoEleDeriv = xp.multiply(1j * muCoEle, arrMultCoEle.T).T

    # another derivative taken in (8) in the EADF paper
    arrMultAziDerivDeriv = xp.multiply(-(muAzi ** 2), arrMultAzi.T).T
    arrMultCoEleDerivDeriv = xp.multiply(-(muCoEle ** 2), arrMultCoEle.T).T

    # build up array of gradient by calling the pattern transform
    # twice and then stacking them along a new last dimension
    d11 = _inversePatternTransformNarrowBand(
        arrMultAziDerivDeriv, arrMultCoEle, arrData, xp
    )
    d22 = _inversePatternTransformNarrowBand(
        arrMultAzi, arrMultCoEleDerivDeriv, arrData, xp
    )
    d12 = _inversePatternTransformNarrowBand(
        arrMultAziDeriv, arrMultCoEleDeriv, arrData, xp
    )

    # this should return
    #     |d11|d12|
    # H = |---|---|
    #     |d12|d22|
    return xp.stack(
        (xp.stack((d11, d12), axis=-1), xp.stack((d12, d22), axis=-1),),
        axis=-1,
    )


def evaluateHessian(
    arrAzi: np.ndarray,
    arrCoEle: np.ndarray,
    arrFreq: np.ndarray,
    muAzi: np.ndarray,
    muCoEle: np.ndarray,
    muFreq: np.ndarray,
    arrData: np.ndarray,
    xp,
) -> np.ndarray:
    """Sample the Beampattern Gradients at Dedicated Angles

    Parameters
    ----------
    arrAzi : np.ndarray
        azimuth angles to sample at in radians
    arrCoEle : np.ndarray
        co-elevation angles to sample at in radians
    arrFreq : np.ndarray
        frequencies to sample at in Hertz
    muAzi : np.ndarray
        spatial frequency bins in azimuth direction
    muCoEle : np.ndarray
        spatial frequency bins in co-elevation direction
    muFreq : np.ndarray
        spatial frequency bins in excitation frequency direction
    arrData : np.ndarray
        fourier coefficients

    Returns
    -------
        np.ndarray
    """
    # equation (7) in the EADF Paper
    arrMultAzi = xp.exp(1j * xp.outer(muAzi, arrAzi))
    arrMultCoEle = xp.exp(1j * xp.outer(muCoEle, arrCoEle))
    arrMultFreq = xp.exp(1j * xp.outer(muFreq, arrFreq))

    # equation (8) in the EADF Paper
    arrMultAziDeriv = xp.multiply(1j * muAzi, arrMultAzi.T).T
    arrMultCoEleDeriv = xp.multiply(1j * muCoEle, arrMultCoEle.T).T
    arrMultFreqDeriv = xp.multiply(1j * muFreq, arrMultFreq.T).T

    # another derivative taken in (8) in the EADF paper
    arrMultAziDerivDeriv = xp.multiply(-(muAzi ** 2), arrMultAzi.T).T
    arrMultCoEleDerivDeriv = xp.multiply(-(muCoEle ** 2), arrMultCoEle.T).T
    arrMultFreqDerivDeriv = xp.multiply(-(muFreq ** 2), arrMultFreq.T).T

    # build up array of gradient by calling the pattern transform
    # twice and then stacking them along a new last dimension
    d11 = _inversePatternTransform(
        arrMultAziDerivDeriv, arrMultCoEle, arrMultFreq, arrData, xp
    )
    d22 = _inversePatternTransform(
        arrMultAzi, arrMultCoEleDerivDeriv, arrMultFreq, arrData, xp
    )
    d12 = _inversePatternTransform(
        arrMultAziDeriv, arrMultCoEleDeriv, arrMultFreq, arrData, xp
    )
    d13 = _inversePatternTransform(
        arrMultAziDeriv, arrMultCoEle, arrMultFreqDeriv, arrData, xp
    )
    d23 = _inversePatternTransform(
        arrMultAzi, arrMultCoEleDeriv, arrMultFreqDeriv, arrData, xp
    )

    d33 = _inversePatternTransform(
        arrMultAzi, arrMultCoEle, arrMultFreqDerivDeriv, arrData, xp
    )

    # this should return
    #     |d11|d12|d13|
    #     |---|---|---|
    # H = |d12|d22|d23|
    #     |---|---|---|
    #     |d13|d23|d33|
    return xp.stack(
        (
            xp.stack((d11, d12, d13), axis=-1),
            xp.stack((d12, d22, d23), axis=-1),
            xp.stack((d13, d23, d33), axis=-1),
        ),
        axis=-1,
    )


def symmetrizeData(arrA: np.ndarray) -> np.ndarray:
    """Generate a symmetrized version of a regularly sampled array data

    This function assumes that we are given the beam pattern sampled in
    co-elevation and azimuth on a regular grid, as well as for at most 2
    polarizations and all the same wave-frequency bins. Then this function
    applies (2) in the original EADF paper. So the resulting array has
    the same dimensions but 2*n-1 the size in co-elevation direction, if
    n was the original co-elevation size.

    Parameters
    ----------
    arrA : np.ndarray
        Input data (co-elevation x azimuth x pol x freq x elem).

    Returns
    -------
    np.ndarray
        Output data (2*co-elevation - 2 x azimuth x pol x freq x elem).

    """
    if len(arrA.shape) != 5:
        logging.error(
            "symmetrizeData: got %d dimensions instead of 5"
            % (len(arrA.shape))
        )
        return

    arrRes = np.tile(arrA, (2, 1, 1, 1, 1))[:-2]

    for ii in range(arrA.shape[2]):
        for jj in range(arrA.shape[3]):
            for kk in range(arrA.shape[4]):
                # Equation (2) in EADF Paper by Landmann and DGO
                # or more correctly the equations (3.13) - (3.17) in the
                # dissertation of Landmann
                arrRes[arrA.shape[0] :, :, ii, jj, kk] = -np.roll(
                    np.flip(arrA[1:-1, :, ii, jj, kk], axis=0),
                    shift=int((arrA.shape[1] - (arrA.shape[1] % 2)) / 2),
                    axis=1,
                )

    return arrRes


def regularSamplingToGrid(
    arrA: np.ndarray, numAzi: int, numCoEle: int
) -> np.ndarray:
    """Reshape an array sampled on a 2D grid to actual 2D data

    Parameters
    ----------
    arrA : np.ndarray
        Input data `arrA` (2D angle x pol x freq x elem).
    numAzi : int
        Number of samples in azimuth direction.
    numCoEle : int
        Number of samples in co-elevation direction.

    Returns
    -------
    np.ndarray
        Output data (co-elevation x azimuth x freq x pol x elem).

    """
    if arrA.shape[0] != (numAzi * numCoEle):
        logging.error(
            (
                "regularSamplingToGrid:"
                + "numAzi %d, numCoEle %d and arrA.shape[0] %d dont match"
            )
            % (numAzi, numCoEle, arrA.shape[0])
        )
        return
    if len(arrA.shape) != 4:
        logging.error(
            (
                "regularSamplingToGrid:"
                + "Input arrA has %d dimensions instead of 4"
            )
            % (len(arrA.shape))
        )
        return

    arrRes = np.empty((numCoEle, numAzi, *arrA.shape[1:]), dtype=arrA.dtype)

    # TODO: How can we speed this up?
    for ii in range(arrA.shape[1]):
        for jj in range(arrA.shape[2]):
            for kk in range(arrA.shape[3]):
                arrRes[:, :, ii, jj, kk] = arrA[:, ii, jj, kk].reshape(
                    (numCoEle, numAzi)
                )

    return arrRes
