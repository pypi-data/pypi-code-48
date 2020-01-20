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
Internal Properties
^^^^^^^^^^^^^^^^^^^

- _arrIndAziCompress: subselection index array in azimuth frequency used during
  compression of the beampattern
- _arrIndCoEleCompress: subselection index array in elevation frequency used
  during compression of the beampattern
- _arrAzi: -> arrAzi
- _arrCoEle: -> arrCoEle
- _arrFreq: -> arrFreq
- _numElements: -> numElements
- _arrFourierData: Fourier data generated upon initialisation
- _arrPos: -> arrPos
- _arrRawData: -> arrRawData
- _dtype -> dtype
- _complexDtype: data type used for complex numbers based on dtype
- _realDtype: data type used for real numbers based on dtype
- _compressionFactor: -> compressionFactor
- _arrDataCalc: data used for actually calculating the beam pattern
- _muAziCalc: data used for actually calculating the beam pattern
- _muCoEleCalc: data used for actually calculating the beam pattern
- _arrFreqCalc: data used for actually calculating the beam pattern
- _useGPU: -> useGPU
- _be: represents either numpy or cupy as backend
- _isNarrowBand -> isNarrowBand
- _version -> version
- _numFreqPadding: how many samples we add in direction of frequency
EADF Object
^^^^^^^^^^^

The EADF object can be used to represent wideband or narrowband antenna
beampatterns.
"""

from . import __version__
import numpy as np
import logging
import pickle
from .core import evaluatePattern
from .core import evaluatePatternNarrowBand
from .core import evaluateGradient
from .core import evaluateGradientNarrowBand
from .core import evaluateHessian
from .core import evaluateHessianNarrowBand
from .preprocess import periodifyFreq
from .auxiliary import sampleAngles
from .auxiliary import toGrid
from .core import sampledToFourier
from .core import symmetrizeData
from .plot import plotBeamPattern2D
from .plot import plotBeamPattern3D
from .plot import plotCut2D
from .preprocess import setCompressionFactor


class EADF(object):
    @property
    def arrIndAziCompress(self) -> np.ndarray:
        """Subselection indices for the compressed array in azimuth (ro)

        Returns
        -------
        np.ndarray
            Subselection in spatial Fourier domain in azimuth

        """
        return self._arrIndAziCompress

    @property
    def arrIndCoEleCompress(self) -> np.ndarray:
        """Subselection indices for the compressed array in elevation (ro)

        Returns
        -------
        np.ndarray
            Subselection in spatial Fourier domain in elevation

        """
        return self._arrIndCoEleCompress

    @property
    def arrIndFreqCompress(self) -> np.ndarray:
        """Subselection indices for the compressed array in ex. freq. (ro)

        Returns
        -------
        np.ndarray
            Subselection in spatial Fourier domain in excitation frequency

        """
        return self._arrIndFreqCompress

    @property
    def arrAzi(self) -> np.ndarray:
        """Return Array Containing the sampled Azimuth Angles

        Returns
        -------
        np.ndarray
            Sampled Azimuth Angles in radians

        """
        return self._arrAzi

    @property
    def arrCoEle(self) -> np.ndarray:
        """Return Array Containing the sampled Co-Elevation Angles

        Returns
        -------
        np.ndarray
            Sampled Co-Elevation Angles in radians

        """
        return self._arrCoEle

    @property
    def arrFreq(self) -> np.ndarray:
        """Return Array Containing the Sampled Frequencies

        Returns
        -------
        np.ndarray
            Sampled Frequencies in Hertz

        """
        return self._arrFreq

    @property
    def numElements(self) -> int:
        """Number of Array Elements (read only)

        Returns
        -------
        int
            Number of Antenna Elements / Ports

        """
        return self._numElements

    @property
    def arrFourierData(self) -> np.ndarray:
        """Return the Fourier Data used to represent the antenna. (read only)

        This is the data after compression with the original data type

        Returns
        -------
        np.ndarray
            2D/3D Fourier Data (compressed)
        """

        return self._arrFourierData[:, self.arrIndAziCompress][
            self.arrIndCoEleCompress
        ][:, :, self.arrIndFreqCompress]

    @property
    def arrRawFourierData(self) -> np.ndarray:
        """Return the Fourier Data used to represent the antenna. (read only)

        This is the data before compression with the original data type

        Returns
        -------
        np.ndarray
            2D Fourier Data (uncompressed)
        """

        return self._arrFourierData

    @property
    def arrPos(self) -> np.ndarray:
        """Positions of the Elements as 3 x numElements

        Returns
        -------
        np.ndarray
            Positions of the Elements as 3 x numElements

        """

        return self._arrPos

    @property
    def arrRawData(self) -> np.ndarray:
        """Return the Raw Data used during construction. (read only)

        Returns
        -------
        np.ndarray
            Raw Data in 2 * Co-Ele x Azi x Freq x Pol x Element
        """

        return self._arrRawData

    @property
    def dtype(self) -> str:
        """Data Type to use during calculations

        Returns
        -------
        str
            either 'float' for single precision or 'double' for
            double precision
        """

        return self._dtype

    @dtype.setter
    def dtype(self, dtype: str) -> None:
        """Set the Data Type

        Parameters
        ----------
        dtype : str
            either 'float' for single precision or 'double' for
            double precision
        """

        if dtype == "float":
            self._complexDtype = "complex64"
            self._realDtype = "float32"
            self._dtype = "float"
        elif dtype == "double":
            self._complexDtype = "complex128"
            self._realDtype = "float64"
            self._dtype = "double"
        else:
            logging.error("dtype: datatype not implemented.")
            return

        # recache the calculation data we use during the beam pattern
        # transform
        self._cacheCalculationData()

    @property
    def isNarrowBand(self) -> None:
        """Return if the current EADF object represents a narrowband Array
        """
        return self._isNarrowBand

    @property
    def useGPU(self) -> None:
        """Return if the current EADF object uses the GPU
        """
        return self._useGPU

    @property
    def version(self) -> None:
        """Return the version of the EADF package used to create the object

        This is important, if we pickle an EADF object and recreate it from
        disk with a possible API break between two versions of the package.
        Right now we only use the property to issue a warning to the user
        when the versions dont match when reading an object from disk.
        """
        return self._version

    @useGPU.setter
    def useGPU(self, flag: int) -> None:
        """Setter to activate the GPU

        If it is set from False to True we try to import cupy, if that fails
        we issue a warning and continue with numpy. If not, we import cupy
        and already cache all the needed data on the GPU.

        Keep in mind that the returned arrays from the evaluation functions
        are left as cupy.ndarrays to simplify further processing on the gpu.

        Parameters
        ----------
        flag : bool
            True or False
        """
        # save the current flag for later comparison
        oldFlag = self._useGPU

        if flag:
            # try importing cupy
            try:
                self._be = __import__("cupy")
                self._useGPU = True
            except ImportError:
                # if this fails, we continue with numpy
                self._be = __import__("numpy")
                self._useGPU = False
                logging.warning("useGPU:cupy not installed. Will use the CPU.")
                return
        else:
            self._be = __import__("numpy")
            self._useGPU = False

        # if something changed copy everything to the GPU (False -> True)
        # or pull it back to the CPU (True -> False)
        if self._useGPU != oldFlag:
            self._cacheCalculationData()

    @property
    def be(self) -> None:
        """Return the currently used computation backend

        This can either be numpy or cupy.
        """
        return self._be

    @property
    def compressionFactor(self) -> float:
        """Compression Factor

        Returns
        -------
        float
            Compression factor in (0,1]

        """
        return self._compressionFactor

    @compressionFactor.setter
    def compressionFactor(self, numValue: float) -> None:
        """Set the Compression Factor

        The EADF allows to reduce the number of parameters of a given
        beampattern by reducing the number of Fourier coefficients.
        This should be done carefully, since one should not throw away
        necessary information. So, we define a compression factor 'p', which
        determines how much 'energy' the remaining Fourier coefficients
        contain.
        So we have the equation: E_c = p * E, where 'E' is the energy of the
        uncompressed array.

        Parameters
        ----------
        numValue : float
            Factor to be set. Must be in (0,1]. The actual subselection
            is done such that the remaining energy is always greater or
            equal than the specified value, which minimizes the expected
            computation time.

        """
        if (numValue <= 0.0) or (numValue > 1.0):
            logging.error("Supplied Value must be in (0, 1]")
        else:
            tplRes = setCompressionFactor(
                self._arrFourierData,
                self._numAziInit,
                self._numCoEleInit,
                self._numFreqInit,
                self._isNarrowBand,
                numValue,
            )

            if self._isNarrowBand:
                # in the narrowband case, we do not subselect in frequency
                # domain, so we append an array that selects all
                # excitation
                tplRes = tplRes + (np.arange(self._arrFreq.shape[0]),)

            (
                self._compressionFactor,
                self._arrIndCoEleCompress,
                self._arrIndAziCompress,
                self._arrIndFreqCompress,
            ) = tplRes

            # recache the calculation data we use during the beam pattern
            # transform
            self._cacheCalculationData()

    def _cacheCalculationData(self) -> None:
        """Cache the actually used calculation data

        This method is the central hub, to keep calculation data
        in the correct data format and in the correct memory (device/host).
        So it should be extended for any new functionality of the class
        that depends on possibly changing data or that introduces parameters
        that influence the calculation.
        """

        self._arrDataCalc = self._be.asarray(
            self.arrFourierData.astype(self._complexDtype)
        )
        self._muAziCalc = self._be.asarray(
            self._muAzi[self._arrIndAziCompress].astype(self._realDtype)
        )
        self._muCoEleCalc = self._be.asarray(
            self._muCoEle[self._arrIndCoEleCompress].astype(self._realDtype)
        )

        if not self._isNarrowBand:
            self._muFreqCalc = self._be.asarray(
                self._muFreq[self._arrIndFreqCompress].astype(self._realDtype)
            )

    def _eval(
        self,
        arrAzi: np.ndarray,
        arrCoEle: np.ndarray,
        arrFreq: np.ndarray,
        funCall,
    ) -> np.ndarray:
        """Unified Evaluation Function

        This function allows to calculate the Hessian, gradient
        and the values themselves with respect to the parameters
        angle and frequency.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        arrFreq : np.ndarray
            Sample at these frequencies in Hertz
        funCall : function
            evaluatePattern, evaluateGradient, evaluateHessian

        Returns
        -------
        np.ndarray
            [description]
        """

        if self.isNarrowBand:
            logging.error("This array is narrowband. Cannot use this function")
            return

        # convert the given inputs to the current datatype
        # nothing is copied, if everything is already on the host / the
        # GPU respectively
        arrAzi = self._be.asarray(arrAzi.astype(self._realDtype))
        arrCoEle = self._be.asarray(arrCoEle.astype(self._realDtype))
        arrFreq = self._be.array(arrFreq).astype(self._realDtype)

        # normalize the physical frequency values to the virtual
        # values between 0 and 2pi * NF / (NF + P)
        arrFreq -= self._arrFreq[0]
        arrFreq /= self._arrFreq[-1] - self._arrFreq[0]
        arrFreq *= (
            2
            * np.pi
            * (self._arrFreq.shape[0] - 1)
            / (self._arrFreq.shape[0] + self._numFreqPadding)
        )

        return funCall(
            arrAzi,
            arrCoEle,
            arrFreq,
            self._muAziCalc,
            self._muCoEleCalc,
            self._muFreqCalc,
            self._arrDataCalc,
            self._be,
        )

    def _evalNarrowBand(
        self,
        arrAzi: np.ndarray,
        arrCoEle: np.ndarray,
        numFreq: float,
        funCall,
    ) -> np.ndarray:
        """Unified Narrowband Evaluation Function

        This function allows to calculate the Hessian, gradient
        and the values themselves with respect to the parameters
        angle for a single frequency.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        numFreq : np.ndarray
            Sample at this frequency in Hertz
        funCall : function
            evaluatePattern, evaluateGradient, evaluateHessian

        Returns
        -------
        np.ndarray
            pattern/gradient/hessian
        """

        if arrAzi.shape[0] != arrCoEle.shape[0]:
            logging.error(
                "patternNarrowBand: supplied angle arrays have size %d and %d."
                % (arrAzi.shape[0], arrCoEle.shape[0])
            )
            return

        if self._isSingleFreq:
            if numFreq != self._arrFreq[0]:
                logging.error(
                    "Desired freq %f does not match sampled one %f"
                    % (numFreq, self._arrFreq[0])
                )
                return
            data = self._arrDataCalc[:, :, 0, :, :]
        else:
            # check if the supplied frequency is in the range we used during
            # the construction
            if (numFreq < np.min(self._arrFreq)) or (
                numFreq > np.max(self._arrFreq)
            ):
                logging.error("Desired freq must be in excitation range.")
                return

            # if the required frequency is among the excitation
            # frequencies, we dont need to interpolate
            if numFreq in self._arrFreq:

                # we simply pick the index in the data array that matches
                # the desired frequency
                numInd = np.arange(self._arrFreq.shape[0])[
                    self._arrFreq == numFreq
                ][0]

                data = self._arrDataCalc[:, :, numInd, :, :]
            else:
                # highest index, such that the excitation frequencies
                # are lower than the requested one.
                numInd = np.arange(self._arrFreq.shape[0])[
                    self._arrFreq <= numFreq
                ][-1]

                # calculate the weighting coefficients of the patterns for
                # neighbouring frequency bins
                a1 = (self._arrFreq[numInd + 1] - numFreq) / (
                    self._arrFreq[numInd + 1] - self._arrFreq[numInd]
                )
                a2 = (numFreq - self._arrFreq[numInd]) / (
                    self._arrFreq[numInd + 1] - self._arrFreq[numInd]
                )

                # here we supply the linearly interpolated data directly
                # thus reducing the EADF computation again to 1 call.
                data = (
                    a1 * self._arrDataCalc[:, :, numInd, :, :]
                    + a2 * self._arrDataCalc[:, :, numInd + 1, :, :]
                )

        # copy everything to device/host ram
        arrAzi = self._be.asarray(arrAzi.astype(self._realDtype))
        arrCoEle = self._be.asarray(arrCoEle.astype(self._realDtype))

        return funCall(
            arrAzi,
            arrCoEle,
            self._muAziCalc,
            self._muCoEleCalc,
            data,
            self._be,
        )

    def patternNarrowBand(
        self, arrAzi: np.ndarray, arrCoEle: np.ndarray, numFreq: float
    ) -> np.ndarray:
        """Sample the Beampattern at Angles and a single Frequency

        The supplied arrays need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for given angles and excitation frequencies
        for all polarizations and array elements.
        So it yields a (Ang,Freq) x Pol x Element ndarray.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequency has to be between the
        minimum and maximum frequency the array was excited with.

        .. note::
          If the GPU is used for calculation a cupy.ndarray is returned,
          so for further processing on the host, you need to copy ot yourself.
          otherwise you can simply continue on the GPU device. Moreover,
          if you supply cupy.ndarrays with the right data types,
          this also speeds up the computation, since no copying or
          conversion have to be done.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        numFreq : np.ndarray
            Sample at this frequency in Hertz

        Returns
        -------
        np.ndarray
            (Ang x Pol x Elem)
        """
        return self._evalNarrowBand(
            arrAzi, arrCoEle, numFreq, evaluatePatternNarrowBand
        )

    def gradientNarrowBand(
        self, arrAzi: np.ndarray, arrCoEle: np.ndarray, numFreq: float
    ) -> np.ndarray:
        """Sample the Beampattern Gradient at Angles and a single Frequency

        The supplied arrays need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for given angles and excitation frequencies
        for all polarizations and array elements.
        So it yields a (Ang,Freq) x Pol x Element ndarray.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequency has to be between the
        minimum and maximum frequency the array was excited with.

        .. note::
          If the GPU is used for calculation a cupy.ndarray is returned,
          so for further processing on the host, you need to copy ot yourself.
          otherwise you can simply continue on the GPU device. Moreover,
          if you supply cupy.ndarrays with the right data types,
          this also speeds up the computation, since no copying or
          conversion have to be done.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        numFreq : np.ndarray
            Sample at this frequency in Hertz

        Returns
        -------
        np.ndarray
            (Ang x Pol x Elem x 2)
        """
        return self._evalNarrowBand(
            arrAzi, arrCoEle, numFreq, evaluateGradientNarrowBand
        )

    def hessianNarrowBand(
        self, arrAzi: np.ndarray, arrCoEle: np.ndarray, numFreq: float
    ) -> np.ndarray:
        """Sample the Beampattern Hessian at Angles and a single Frequency

        The supplied arrays need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for given angles and excitation frequencies
        for all polarizations and array elements.
        So it yields a (Ang,Freq) x Pol x Element ndarray.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequency has to be between the
        minimum and maximum frequency the array was excited with.

        .. note::
          If the GPU is used for calculation a cupy.ndarray is returned,
          so for further processing on the host, you need to copy ot yourself.
          otherwise you can simply continue on the GPU device. Moreover,
          if you supply cupy.ndarrays with the right data types,
          this also speeds up the computation, since no copying or
          conversion have to be done.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        numFreq : np.ndarray
            Sample at this frequency in Hertz

        Returns
        -------
        np.ndarray
            (Ang x Pol x Elem x 2 x 2)
        """
        return self._evalNarrowBand(
            arrAzi, arrCoEle, numFreq, evaluateHessianNarrowBand
        )

    def pattern(
        self, arrAzi: np.ndarray, arrCoEle: np.ndarray, arrFreq: np.ndarray
    ) -> np.ndarray:
        """Sample the Beampattern at Angles and Frequencies

        The supplied arrays need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for given angles and excitation frequencies
        for all polarizations and array elements.
        So it yields a (Ang,Freq) x Pol x Element ndarray.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequencies have to be between the
        minimum and maximum frequency the array was excited with.

        .. note::
          If the GPU is used for calculation a cupy.ndarray is returned,
          so for further processing on the host, you need to copy ot yourself.
          otherwise you can simply continue on the GPU device. Moreover,
          if you supply cupy.ndarrays with the right data types,
          this also speeds up the computation, since no copying or
          conversion have to be done.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        arrFreq : np.ndarray
            Sample at these frequencies in Hertz

        Returns
        -------
        np.ndarray
            Beampattern values at the requested angles
            ((Ang, Freq) x Pol x Elem)
        """

        return self._eval(arrAzi, arrCoEle, arrFreq, evaluatePattern)

    def gradient(
        self, arrAzi: np.ndarray, arrCoEle: np.ndarray, arrFreq: np.ndarray
    ) -> np.ndarray:
        """Sample the Beampattern Gradient at Angles and Frequencies

        The supplied arrays need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for given angles and excitation frequencies
        for all polarizations and array elements.
        So it yields a (Ang,Freq) x Pol x Element ndarray.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequencies have to be between the
        minimum and maximum frequency the array was excited with.

        .. note::
          If the GPU is used for calculation a cupy.ndarray is returned,
          so for further processing on the host, you need to copy ot yourself.
          otherwise you can simply continue on the GPU device. Moreover,
          if you supply cupy.ndarrays with the right data types,
          this also speeds up the computation, since no copying or
          conversion have to be done.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        arrFreq : np.ndarray
            Sample at these frequencies in Hertz

        Returns
        -------
        np.ndarray
            Beampattern gradient values at the requested angles
            ((Ang, Freq) x Pol x Elem x 3)
        """

        return self._eval(arrAzi, arrCoEle, arrFreq, evaluateGradient)

    def hessian(
        self, arrAzi: np.ndarray, arrCoEle: np.ndarray, arrFreq: np.ndarray
    ) -> np.ndarray:
        """Sample the Beampattern Hessian at Angles and Frequencies

        The supplied arrays need to have the same length. The returned
        array has again the same length. This method samples the EADF object
        for given angles and excitation frequencies
        for all polarizations and array elements.
        So it yields a (Ang,Freq) x Pol x Element ndarray.

        Since we have no crystalline sphere to guess, we cannot do
        extrapolation, so the requested frequencies have to be between the
        minimum and maximum frequency the array was excited with.

        .. note::
          If the GPU is used for calculation a cupy.ndarray is returned,
          so for further processing on the host, you need to copy ot yourself.
          otherwise you can simply continue on the GPU device. Moreover,
          if you supply cupy.ndarrays with the right data types,
          this also speeds up the computation, since no copying or
          conversion have to be done.

        Parameters
        ----------
        arrAzi : np.ndarray
            Sample at these azimuths in radians
        arrCoEle : np.ndarray
            Sample at these elevations in radians
        arrFreq : np.ndarray
            Sample at these frequencies in Hertz

        Returns
        -------
        np.ndarray
            Beampattern gradient values at the requested angles
            ((Ang, Freq) x Pol x Elem x 3 x 3)
        """

        return self._eval(arrAzi, arrCoEle, arrFreq, evaluateHessian)

    def visualizeCut(
        self,
        numAzi: int,
        numCoEle: float,
        numPol: list,
        numFreq: float,
        arrIndElem: list,
        fun=None,
    ) -> None:
        """Visualize the Beampattern Along a Certain Angle of Co-Elevation

        This plots several beam patterns along one co-elevation level.
        It also positions the elements in the correct 2D-position from top
        down.

        Example
        -------
        >>> import eadf
        >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
        >>> A.visualizeCut(
        >>>     60, 1.67, [0], A.arrFreq[0], list(range(11))
        >>> )

        Parameters
        ----------
        numAzi : int
            Number of regularly spaced azimuth grid points
        numCoEle : float
            Co-Elevation angle to make the cut at in radians
        numPol : list
            Can be either [0], [1] or [0,1]. Selects the polarizations
        numFreq : float
            Freqency to plot
        arrIndElem : list
            Antenna elements to plot
        fun : method
            function to apply to the elements values
            right before plotting. popular choices are np.real or np.imag
            if not specified we use np.abs( . )

        """

        # sample the angles on a regular grid
        arrAzi, arrCoEle = sampleAngles(numAzi, 1, lstEndPoints=[True, False])

        # set the elevation angle array to the specified elevation
        # angle
        arrCoEle[:] = numCoEle

        # now generate the grid
        grdAzi, grdCoEle = toGrid(arrAzi, arrCoEle)

        # now sample the array values on the grid
        arrPlotData = self.pattern(grdAzi, grdCoEle, numFreq)

        # copy back to host to plot it
        if self._useGPU:
            arrPlotData = self._be.asarray(arrPlotData)

        plotCut2D(
            # now subselect the samples values to the specified
            # polarisation, elements and frequency (the 0)
            arrPlotData[:, numPol, arrIndElem].reshape(
                (-1, 1, len(arrIndElem))
            ),
            grdAzi,
            self._arrPos[:, arrIndElem],
            fun,
        )

    def visualize2D(
        self,
        numAzi: int,
        numCoEle: int,
        numPol: int,
        numFreq: float,
        arrIndElem: list,
        fun=None,
    ) -> None:
        """Plot an Image of several Elements' Beampatterns

        Example
        -------

        >>> import eadf
        >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
        >>> A.visualize2D(40, 20, 0, A.arrFreq[0], [0])

        Parameters
        ----------
        numAzi : int
            number of samples in azimuth direction
        numCoEle : int
            number of samples in co-elevation direction
        numPol : int
            polarisation 0, or 1?
        numFreq : float
            Frequency to plot at
        arrIndElem : list
            Index of element to visualize
        fun : method
            function to apply to the elements values
            right before plotting. popular choices are np.real or np.imag
            if not specified we use np.abs( . )
        """

        arrAzi, arrCoEle = sampleAngles(
            numAzi, numCoEle, lstEndPoints=[True, True]
        )
        grdAzi, grdCoEle = toGrid(arrAzi, arrCoEle)
        arrPlotData = self.pattern(grdAzi, grdCoEle, numFreq)

        # copy back to host to plot it
        if self._useGPU:
            arrPlotData = self._be.asarray(arrPlotData)

        plotBeamPattern2D(
            arrPlotData[:, numPol, arrIndElem],
            grdAzi,
            grdCoEle,
            numAzi,
            numCoEle,
        )

    def visualize3D(
        self,
        numAzi: int,
        numCoEle: int,
        numPol: int,
        numFreq: float,
        arrIndElem: list,
        fun=None,
    ) -> None:
        """Plot the Array with 3D Beampatterns

        We first sample the array for on a regular grid in co-elevation
        and azimuth and then we put deformed spheres at the elements
        positions to represent the array elements. for this a fixed
        polarization and a fixed wave-frequency have to be selected.

        Example
        -------

        >>> import eadf
        >>> A = eadf.arrays.generateStackedUCA(11, 3, 1.5, 0.5)
        >>> A.visualize3D(40, 20, 0, 1, [0])

        Parameters
        ----------
        numAzi : int
            number of samples in azimuth direction
        numCoEle : int
            number of samples in co-elevation direction
        numPol : int
            polarisation 0, or 1?
        numFreq : float
            Frequency to sample at
        arrIndElem : list
            Element index to visualize
        fun : method
            function to apply to the elements values
            right before plotting. popular choices are np.real or np.imag
            if not specified we use np.abs( . )
        """

        arrAzi, arrCoEle = sampleAngles(
            numAzi, numCoEle, lstEndPoints=[True, True]
        )
        grdAzi, grdCoEle = toGrid(arrAzi, arrCoEle)
        arrPlotData = self.pattern(grdAzi, grdCoEle, numFreq)

        # copy back to host to plot it
        if self._useGPU:
            arrPlotData = self._be.asarray(arrPlotData)

        plotBeamPattern3D(
            arrPlotData[:, numPol, arrIndElem],
            grdAzi,
            grdCoEle,
            self._arrPos[:, arrIndElem],
            numAzi,
            numCoEle,
            fun=(lambda c: np.abs(c) ** 2),
        )

    def __getstate__(self):
        # Copy the object's state from self.__dict__ which contains
        # all our instance attributes. Always use the dict.copy()
        # method to avoid modifying the original state.
        state = self.__dict__.copy()
        del state["_be"]
        return state

    def __setstate__(self, state):
        # Restore instance attributes
        self.__dict__.update(state)

        # reimport the backend appropriately
        # by trying to recover the old state
        # this might result in a different backend as before
        # depending on availability of hardware and cupy
        self.useGPU = self.__dict__["_useGPU"]

    def save(self, path: str) -> None:
        """Save the object to disk in a serialized way

        .. note::
            This is not save! Make sure the requirements for pickling are met.
            Among these are different CPU architectures, Python versions,
            Numpy versions and so forth.

            However we at least check the eadf package version when reading
            back from disk.

        Parameters
        ----------
        path : str
            Path to write to
        """
        with open(path, "wb") as file:
            pickle.dump(self, file)

    @classmethod
    def load(cls, path: str) -> object:
        """Load the Class from Serialized Data

        .. note::
            This is not save! Make sure the requirements for pickling are met.
            Among these are different CPU architectures, Python versions,
            Numpy versions and so forth.

            However we at least check the eadf package version when reading
            back from disk and issue a warning if the versions don't match.
            then you are on your own!

        Parameters
        ----------
        path : str
            Path to load from

        Returns
        -------
        object
            The EADF object
        """
        with open(path, "rb") as file:
            res = pickle.load(file)

        from . import __version__

        if res.version != __version__:
            logging.warning(
                "eadf.load: loaded object does not match current version."
            )
        return res

    def __init__(
        self,
        arrData: np.ndarray,
        arrAzi: np.ndarray,
        arrCoEle: np.ndarray,
        arrFreq: np.ndarray,
        arrPos: np.ndarray,
        **options
    ) -> None:
        """Initialize an EADF Object

        Here we assume that the input data is given in the internal data
        format already. If you have antenna data, which is not in the
        internat data format, we advice you to use one of the importers,
        or implement your own.

        In direction of co-elevation, we assume that both the north and the
        south pole were sampled. In azimuth direction, we truncate the last
        sample, if we detect in arrAzi that both -pi and +pi were sampled.

        Parameters
        ----------
        arrData : np.ndarray
            Co-Ele x Azi x Freq x Pol x Element
        arrAzi : np.ndarray
            Azimuth sampling positions in radians.
        arrCoEle : np.ndarray
            Co-elevation sampling positions in radians.
            both poles should be sampled.
        arrFreq : np.ndarray
            Frequencies sampled at.
        arrPos : np.ndarray
            (3 x numElements) Positions of the single antenna elements.
            this is just for vizualisation purposes.
        **options : kwargs
           See the list of general options below.

        options in `**options`
        ----------------------
        keepNarrowBand: bool
            this enforces the array to be treated as a
            collection of narrowband array. So no interpolation along
            frequency is done during preprocessing and one can only
            call the *NarrowBand methods of the instance. Can only be
            used if you are supplying data with arrData.shape[2] > 1.

            Defaults to (arrData.shape[2] == 1)

        numFreqPadding: int
            number of samples to use to periodify in frequency direction
            defaults to 10

        """

        self._isSingleFreq = arrData.shape[2] == 1

        # if we might be tempted to treat the array was wideband data,
        # the user might have set the flag to not do so.
        self._isNarrowBand = options.get("keepNarrowBand", self._isSingleFreq)
        self._numFreqPadding = options.get("numFreqPadding", 10)

        if arrData.shape[1] != arrAzi.shape[0]:
            logging.error(
                "EADF:arrData.shape[1](%d) = arrCoEle.shape[0](%d)"
                % (arrData.shape[1], arrAzi.shape[0])
            )
            return
        if arrData.shape[0] != arrCoEle.shape[0]:
            logging.error(
                "EADF:arrData.shape[0](%d) = arrCoEle.shape[0](%d)"
                % (arrData.shape[0], arrCoEle.shape[0])
            )
            return
        if arrData.shape[2] != arrFreq.shape[0]:
            logging.error(
                "EADF:arrData.shape[2](%d) = arrFreq.shape[0](%d)"
                % (arrData.shape[2], arrFreq.shape[0])
            )
            return
        if arrPos.shape[0] != 3:
            logging.error("EADF:arrPos.shape[0](%d) != 3" % (arrPos.shape[0]))
            return
        if arrPos.shape[1] != arrData.shape[4]:
            logging.error(
                "EADF: num of positions %d doesnt match elem number %d"
                % (arrPos.shape[1], arrData.shape[4])
            )
            return
        if np.any((arrFreq[:-1] - arrFreq[1:]) >= 0):
            logging.error("EADF: frequencies must be sorted")
            return

        # truncate the beampattern data correctly
        # in azimuth we make sure that we did not sample the same angle twice
        if np.allclose(
            np.mod(arrAzi[0] + 2 * np.pi, 2 * np.pi),
            np.mod(arrAzi[-1], 2 * np.pi),
        ):
            arrAziTrunc = np.arange(arrAzi.shape[0] - 1)
        else:
            arrAziTrunc = np.arange(arrAzi.shape[0])

        # in elevation we check if we sampled from north to south pole
        if not np.allclose(arrCoEle[0], 0):
            logging.error("EADF: you must sample at the north pole.")
            return
        if not np.allclose(arrCoEle[-1], np.pi):
            logging.error("EADF: you must sample at the south pole.")
            return

        # make a copy of the supplied data
        self._arrRawData = np.copy(arrData)

        # if we are not narrowband we apply spline extrapolation
        # to make the data in frequency periodic
        if not self._isNarrowBand:
            self._arrRawData = periodifyFreq(
                arrData[:, arrAziTrunc], self._numFreqPadding
            )

        # do the flipping and shifting in elevation and azimuth
        self._arrRawData = symmetrizeData(self._arrRawData)

        # extract some meta data from the input
        self._arrPos = np.copy(arrPos)
        self._numElements = self._arrPos.shape[1]
        self._numAziInit = arrAziTrunc.shape[0]
        self._numCoEleInit = 2 * arrCoEle.shape[0] - 2
        self._arrAzi = np.copy(arrAzi.flatten()[arrAziTrunc])
        self._arrCoEle = np.copy(arrCoEle.flatten())
        self._arrFreq = np.copy(arrFreq.flatten())

        # now we know how many samples exactly we have in frequency
        # direction
        self._numFreqInit = self._arrRawData.shape[2]

        # generate the Fourier representation and the according
        # frequency bins
        if self._isNarrowBand:
            (
                self._arrFourierData,
                self._muCoEle,
                self._muAzi,
            ) = sampledToFourier(self._arrRawData[:, arrAziTrunc], (0, 1))
        else:
            (
                self._arrFourierData,
                self._muCoEle,
                self._muAzi,
                self._muFreq,
            ) = sampledToFourier(self._arrRawData[:, arrAziTrunc], (0, 1, 2))

        # initialize some properties with defaults values
        self._complexDtype = "complex128"
        self._realDtype = "float64"
        self._dtype = "double"
        self._useGPU = False
        self._be = np

        # initially we don't do any compression
        # but this already truncates any zeros in the spectrum
        self.compressionFactor = 1.0
        self.dtype = "double"
        self.useGPU = False

        # so we can start off quickly!
        self._cacheCalculationData()

        # set the version
        self._version = __version__
