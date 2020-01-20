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
from eadf.auxiliary import cartesianToSpherical, columnwiseKron, sampleAngles
from eadf.auxiliary import toGrid


class TestCartesianToSpherical(unittest.TestCase):
    def setUp(self):
        self.arrA = np.random.randn(10, 3)

    def test_success(self):
        cartesianToSpherical(self.arrA)

    @patch("logging.error")
    def test_inputSizeFail(self, mock):
        cartesianToSpherical(self.arrA[:, :2])
        mock.assert_called_with(
            "cartesianToSpherical: arrA has wrong second dimension."
        )

    @patch("logging.error")
    def test_inputTypeFail(self, mock):
        cartesianToSpherical(self.arrA + 1j)
        mock.assert_called_with("cartesianToSpherical: arrA is complex.")


class TestColumnwiseKron(unittest.TestCase):
    def setUp(self):
        self.arrA = np.random.randn(5, 3)
        self.arrB = np.random.randn(7, 3)

    def test_success(self):
        columnwiseKron(self.arrA, self.arrB)

    @patch("logging.error")
    def test_inputSizeFail(self, mock):
        columnwiseKron(self.arrA[:, :2], self.arrB)
        mock.assert_called_with(
            "columnwiseKron: Matrices cannot be multiplied"
        )


class TestSampleAngles(unittest.TestCase):
    def test_sucess1(self):
        sampleAngles(10, 15)

    def test_sucess2(self):
        sampleAngles(10, 15, lstEndPoints=[False, False])

    def test_sucess3(self):
        sampleAngles(10, 15, lstEndPoints=[True, False])

    def test_sucess4(self):
        sampleAngles(10, 15, lstEndPoints=[False, True])

    def test_sucess5(self):
        sampleAngles(10, 15, lstEndPoints=[True, True])

    @patch("logging.error")
    def test_inputFail1(self, mock):
        sampleAngles(-1, 5)
        mock.assert_called_with(
            "sampleAngles: numAzi is %d, must be > 0" % (-1)
        )

    @patch("logging.error")
    def test_inputFail2(self, mock):
        sampleAngles(10, -1)
        mock.assert_called_with(
            "sampleAngles: numCoEle is %d, must be > 0" % (-1)
        )

    @patch("logging.error")
    def test_inputFail3(self, mock):
        sampleAngles(10, 10, lstEndPoints=[False, False, False])
        mock.assert_called_with(
            "sampleAngles: lstEndPoints has length %d instead of 2." % (3)
        )


class TestToGrid(unittest.TestCase):
    def test_success1(self):
        toGrid(np.arange(4), np.arange(5))

    def test_success2(self):
        toGrid(np.arange(4), np.arange(5), np.arange(6))


if __name__ == "__main__":
    unittest.main()
