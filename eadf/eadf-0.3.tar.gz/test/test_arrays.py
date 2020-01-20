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

from eadf.arrays import generateURA
from eadf.arrays import generateULA
from eadf.arrays import generateUCA
from eadf.arrays import generateStackedUCA
from eadf.arrays import generateUniformArbitrary
import unittest
import numpy as np
from unittest.mock import patch


class TestURA(unittest.TestCase):
    def setUp(self):
        self.array = generateURA(5, 6, 0.5, 0.75)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 5 * 6)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 5 * 6))

    @patch("logging.error")
    def test_numElementsXFail(self, mock):
        # must not be negative
        self.array = generateURA(-5, 6, 0.5, 0.5)
        mock.assert_called_with(
            "generateULA: numElementsX <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numSpacingXFail(self, mock):
        self.array = generateURA(5, 6, -0.5, 0.5)
        mock.assert_called_with(
            "generateULA: numSpacingX <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numElementsYFail(self, mock):
        self.array = generateURA(5, -6, 0.5, 0.5)
        mock.assert_called_with(
            "generateULA: numElementsY <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numSpacingYFail(self, mock):
        self.array = generateURA(5, 6, 0.5, -0.5)
        mock.assert_called_with(
            "generateULA: numSpacingY <= 0 is not allowed."
        )


class TestULA(unittest.TestCase):
    def setUp(self):
        self.array = generateULA(11, 0.5)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 11)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 11))

    @patch("logging.error")
    def test_numElementsFail(self, mock):
        self.array = generateULA(-11, 0.5)
        mock.assert_called_with(
            "generateULA: numElements <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numSpacingFail(self, mock):
        self.array = generateULA(11, -0.5)
        mock.assert_called_with("generateULA: numSpacing <= 0 is not allowed.")


class TestUCA(unittest.TestCase):
    def setUp(self):
        self.array = generateUCA(11, 0.5)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 11)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 11))

    @patch("logging.error")
    def test_numElementsFail(self, mock):
        self.array = generateUCA(-11, 0.5)
        mock.assert_called_with(
            "generateUCA: numElements <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numRadiusFail(self, mock):
        self.array = generateUCA(11, -0.5)
        mock.assert_called_with("generateUCA: numRadius <= 0 is not allowed.")


class TestStackedUCA(unittest.TestCase):
    def setUp(self):
        self.array = generateStackedUCA(11, 3, 0.5, 0.5)

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 11 * 3)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 11 * 3))

    @patch("logging.error")
    def test_numElementsFail(self, mock):
        self.array = generateStackedUCA(-11, 3, 0.5, 0.5)
        mock.assert_called_with(
            "generateStackedUCA: numElements <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numStacksFail(self, mock):
        self.array = generateStackedUCA(11, -3, 0.5, 0.5)
        mock.assert_called_with(
            "generateStackedUCA: numStacks <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numRadiusFail(self, mock):
        self.array = generateStackedUCA(11, 3, -0.5, 0.5)
        mock.assert_called_with(
            "generateStackedUCA: numRadius <= 0 is not allowed."
        )

    @patch("logging.error")
    def test_numHeightFail(self, mock):
        self.array = generateStackedUCA(11, 3, 0.5, -0.5)
        mock.assert_called_with(
            "generateStackedUCA: numHeight <= 0 is not allowed."
        )


class TestUniformArbitrary(unittest.TestCase):
    def setUp(self):
        self.array = generateUniformArbitrary(np.random.randn(3, 10))

    def test_numElements(self):
        self.assertEqual(self.array.numElements, 10)

    def test_arrPosSize(self):
        self.assertEqual(self.array.arrPos.shape, (3, 10))

    @patch("logging.error")
    def test_arrPosFail(self, mock):
        generateUniformArbitrary(np.random.randn(2, 10))
        mock.assert_called_with(
            "generateUniformArbitrary: arrPos must have exactly 3 rows"
        )


if __name__ == "__main__":
    unittest.main()
