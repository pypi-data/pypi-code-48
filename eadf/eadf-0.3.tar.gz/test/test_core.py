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
from eadf.core import fourierToSampled, sampledToFourier, symmetrizeData
from eadf.core import regularSamplingToGrid


class TestFourierToSampled(unittest.TestCase):
    def setUp(self):
        self.data = np.random.randn(14, 28, 2, 2, 5) + 1j

    def test_success2D(self):
        fourierToSampled(self.data, (0, 1))

    def test_success3D(self):
        fourierToSampled(self.data, (0, 1, 2))

    @patch("logging.error")
    def test_shapeFail1(self, mock):
        fourierToSampled(self.data[0], (0, 1, 2))
        mock.assert_called_with(
            "fourierToSampled: arrData has wrong number of dimensions"
        )

    @patch("logging.error")
    def test_shapeFail2(self, mock):
        fourierToSampled(np.random.randn(14, 28, 2, 3, 5) + 1j, (0, 1, 2))
        mock.assert_called_with(
            "fourierToSampled: There must be at most 2 polarisations"
        )


class TestSampledToFourier(unittest.TestCase):
    def setUp(self):
        self.data = np.random.randn(14, 28, 2, 2, 5) + 1j

    def test_success2D(self):
        sampledToFourier(self.data, (0, 1))

    def test_success3D(self):
        sampledToFourier(self.data, (0, 1, 2))

    @patch("logging.error")
    def test_shapeFail1(self, mock):
        sampledToFourier(self.data[:3], (0, 1, 2))
        mock.assert_called_with(
            "sampledToFourier: 1st dim of arrData must have even size."
        )

    @patch("logging.error")
    def test_shapeFail2(self, mock):
        sampledToFourier(self.data[0], (0, 1, 2))
        mock.assert_called_with(
            "sampledToFourier: arrData has wrong number of dimensions"
        )

    @patch("logging.error")
    def test_shapeFail3(self, mock):
        sampledToFourier(np.random.randn(14, 28, 2, 3, 5) + 1j, (0, 1, 2))
        mock.assert_called_with(
            "sampledToFourier: There must be at most 2 polarisations"
        )


class TestSymmetrizeData(unittest.TestCase):
    def setUp(self):
        self.data = np.random.randn(14, 28, 2, 3, 5)

    def test_success(self):
        symmetrizeData(self.data)

    @patch("logging.error")
    def test_shapeFail(self, mock):
        symmetrizeData(self.data[0])
        mock.assert_called_with(
            "symmetrizeData: got %d dimensions instead of 5" % (4)
        )


class TestRegularSamplingToGrid(unittest.TestCase):
    def setUp(self):
        self.data = np.random.randn(14 * 13, 2, 3, 5)

    def test_success(self):
        regularSamplingToGrid(self.data, 14, 13)

    @patch("logging.error")
    def test_shapeFail1(self, mock):
        regularSamplingToGrid(self.data[:, :, :, 0], 14, 13)
        mock.assert_called_with(
            (
                "regularSamplingToGrid:"
                + "Input arrA has %d dimensions instead of 4"
            )
            % (len(self.data[:, :, :, 0].shape))
        )

    @patch("logging.error")
    def test_shapeFail2(self, mock):
        regularSamplingToGrid(self.data[:13], 13, 14)
        mock.assert_called_with(
            (
                "regularSamplingToGrid:"
                + "numAzi %d, numCoEle %d and arrA.shape[0] %d dont match"
            )
            % (13, 14, self.data[:13].shape[0])
        )


if __name__ == "__main__":
    unittest.main()
