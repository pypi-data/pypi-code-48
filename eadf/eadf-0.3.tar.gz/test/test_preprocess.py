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

import unittest
from unittest.mock import patch
import numpy as np
from eadf.preprocess import interpolateDataSphere


class TestInterpolateDataSphere(unittest.TestCase):
    def setUp(self):
        self.data = np.random.randn(10, 20)
        self.aziSample = np.random.randn(10)
        self.coEleSample = np.random.randn(10)
        self.aziInter = np.random.randn(20)
        self.coEleInter = np.random.randn(20)

    @patch("logging.error")
    def test_shapeFail1(self, mock):
        interpolateDataSphere(
            self.aziSample,
            self.coEleSample,
            self.data[:-1],
            self.aziInter,
            self.coEleInter,
            method="SH",
        )
        mock.assert_called_with(
            (
                "interpolateDataSphere:"
                + "Input arrays of sizes %d azi, %d ele, %d values dont match"
            )
            % (
                self.aziSample.shape[0],
                self.coEleSample.shape[0],
                self.data.shape[0] - 1,
            )
        )

    @patch("logging.error")
    def test_shapeFail2(self, mock):
        interpolateDataSphere(
            self.aziSample[:-1],
            self.coEleSample,
            self.data,
            self.aziInter,
            self.coEleInter,
            method="SH",
        )
        mock.assert_called_with(
            (
                "interpolateDataSphere:"
                + "Input arrays of sizes %d azi, %d ele, %d values dont match"
            )
            % (
                self.aziSample.shape[0] - 1,
                self.coEleSample.shape[0],
                self.data.shape[0],
            )
        )

    @patch("logging.error")
    def test_shapeFail3(self, mock):
        interpolateDataSphere(
            self.aziSample,
            self.coEleSample,
            self.data,
            self.aziInter[:-1],
            self.coEleInter,
            method="SH",
        )
        mock.assert_called_with(
            (
                "interpolateDataSphere:"
                + "Output arrays of sizes %d azi, %d ele dont match"
            )
            % (self.aziInter.shape[0] - 1, self.coEleInter.shape[0])
        )

    @patch("logging.error")
    def test_methodFail(self, mock):
        interpolateDataSphere(
            self.aziSample,
            self.coEleSample,
            self.data,
            self.aziInter,
            self.coEleInter,
            method="foobar",
        )
        mock.assert_called_with(
            "interpolateDataSphere: Method not implemented."
        )

    @patch("logging.error")
    def test_methodSHNumNFail(self, mock):
        interpolateDataSphere(
            self.aziSample,
            self.coEleSample,
            self.data,
            self.aziInter,
            self.coEleInter,
            method="SH",
            numN=0,
        )
        mock.assert_called_with(
            "interpolateDataSphere:"
            + "_genSHMatrix: numN must be greater than 0."
        )


if __name__ == "__main__":
    unittest.main()
