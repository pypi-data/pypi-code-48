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

import numpy as np
import unittest
from eadf.eadf import EADF
from eadf.auxiliary import toGrid
from eadf.auxiliary import sampleAngles
from eadf.arrays import generateUniformArbitrary
from unittest.mock import patch


class TestInit(unittest.TestCase):
    def setUp(self):
        self.array = generateUniformArbitrary(np.random.randn(3, 11))

        self.data = self.array.patternNarrowBand(
            *toGrid(self.array.arrAzi, self.array.arrCoEle),
            self.array.arrFreq[0]
        ).reshape(
            (
                self.array.arrCoEle.shape[0],
                self.array.arrAzi.shape[0],
                1,
                1,
                11,
            )
        )

    @patch("logging.error")
    def test_arrAziShape(self, mock):
        EADF(
            self.data[:, :-1],
            self.array.arrAzi,
            self.array.arrCoEle,
            self.array.arrFreq,
            self.array.arrPos,
        )
        mock.assert_called_with(
            "EADF:arrData.shape[1](%d) = arrCoEle.shape[0](%d)"
            % (self.data.shape[1] - 1, self.array.arrAzi.shape[0])
        )

    @patch("logging.error")
    def test_arrCoEleShape(self, mock):
        EADF(
            self.data[:-1],
            self.array.arrAzi,
            self.array.arrCoEle,
            self.array.arrFreq,
            self.array.arrPos,
        )
        mock.assert_called_with(
            "EADF:arrData.shape[0](%d) = arrCoEle.shape[0](%d)"
            % (self.data.shape[0] - 1, self.array.arrCoEle.shape[0])
        )

    @patch("logging.error")
    def test_arrFreqShape(self, mock):
        EADF(
            self.data,
            self.array.arrAzi,
            self.array.arrCoEle,
            np.linspace(1, 2, 2),
            self.array.arrPos,
        )
        mock.assert_called_with(
            "EADF:arrData.shape[2](%d) = arrFreq.shape[0](%d)"
            % (self.data.shape[2], self.array.arrFreq.shape[0] + 1)
        )

    @patch("logging.error")
    def test_arrPos1Shape(self, mock):
        EADF(
            self.data,
            self.array.arrAzi,
            self.array.arrCoEle,
            self.array.arrFreq,
            self.array.arrPos[:-1],
        )
        mock.assert_called_with(
            "EADF:arrPos.shape[0](%d) != 3" % (self.array.arrPos.shape[0] - 1)
        )

    @patch("logging.error")
    def test_arrPos2Shape(self, mock):
        EADF(
            self.data,
            self.array.arrAzi,
            self.array.arrCoEle,
            self.array.arrFreq,
            self.array.arrPos[:, :-1],
        )
        mock.assert_called_with(
            "EADF: num of positions %d doesnt match elem number %d"
            % (self.array.arrPos.shape[1] - 1, self.data.shape[4])
        )

    # @patch('logging.error')
    # def test_arrFreqSort(self, mock):
    #     EADF(
    #         self.data,
    #         self.array.arrAzi,
    #         self.array.arrCoEle,
    #         self.array.arrFreq[::-1],
    #         self.array.arrPos
    #     )
    #     mock.assert_called_with(
    #         "EADF: frequencies must be sorted"
    #     )


class TestProperties(unittest.TestCase):
    def setUp(self):
        self.array = generateUniformArbitrary(np.random.randn(3, 11))

    @patch("logging.error")
    def test_arrComFact1(self, mock):
        self.array.compressionFactor = 1.1
        mock.assert_called_with("Supplied Value must be in (0, 1]")

    @patch("logging.error")
    def test_arrComFact2(self, mock):
        self.array.compressionFactor = -1.1
        mock.assert_called_with("Supplied Value must be in (0, 1]")

    @patch("logging.error")
    def test_arrDType(self, mock):
        self.array.dtype = "floaty"
        mock.assert_called_with("dtype: datatype not implemented.")


class TestPatternNarrowBand(unittest.TestCase):
    def setUp(self):
        self.array = generateUniformArbitrary(np.random.randn(3, 11))
        self.arrAzi, self.arrCoEle = toGrid(*sampleAngles(10, 5))

    def test_success_pattern(self):
        self.array.patternNarrowBand(
            self.arrAzi, self.arrCoEle, self.array.arrFreq[0]
        )

    def test_success_gradient(self):
        self.array.gradientNarrowBand(
            self.arrAzi, self.arrCoEle, self.array.arrFreq[0]
        )

    def test_success_hessian(self):
        self.array.hessianNarrowBand(
            self.arrAzi, self.arrCoEle, self.array.arrFreq[0]
        )

    @patch("logging.error")
    def test_inputSizeFail(self, mock):
        self.array.patternNarrowBand(
            self.arrAzi, self.arrCoEle[:-1], self.array.arrFreq[0]
        )
        mock.assert_called_with(
            "patternNarrowBand: supplied angle arrays have size %d and %d."
            % (self.arrAzi.shape[0], self.arrCoEle[:-1].shape[0])
        )

    @patch("logging.error")
    def test_freqFail(self, mock):
        self.array.patternNarrowBand(
            self.arrAzi, self.arrCoEle, self.array.arrFreq[0] + 1
        )
        mock.assert_called_with(
            "Desired freq %f does not match sampled one %f"
            % (self.array._arrFreq[0] + 1, self.array._arrFreq[0])
        )


class TestSerialization(unittest.TestCase):
    def setUp(self):
        self.array = generateUniformArbitrary(np.random.randn(3, 11))

    def test_save_success(self):
        self.array.save("test.dat")

    def test_load_success(self):
        self.array.save("test.dat")
        arrayLoad = EADF.load("test.dat")

    @patch("logging.warning")
    def test_load_version_warn(self, mock):
        self.array._version += "bla"
        self.array.save("test.dat")
        arrayLoad = EADF.load("test.dat")
        mock.assert_called_with(
            "eadf.load: loaded object does not match current version."
        )


if __name__ == "__main__":
    unittest.main()
