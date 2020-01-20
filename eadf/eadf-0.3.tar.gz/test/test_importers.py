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
from eadf.importers import fromAngleListData
from eadf.arrays import generateUCA
from eadf.auxiliary import sampleAngles, toGrid
import numpy as np


class TestFromAngleListData(unittest.TestCase):
    def setUp(self):
        self.array = generateUCA(13, 1.2)
        self.arrAziS, self.arrCoEleS = toGrid(*sampleAngles(40, 20))
        self.arrAziI, self.arrCoEleI = toGrid(*sampleAngles(60, 30))

        # we need the frequency dimension
        self.dataS = self.array.patternNarrowBand(
            self.arrAziS, self.arrCoEleS, self.array.arrFreq[0]
        )[:, np.newaxis, np.newaxis, :]

    @patch("logging.error")
    def test_inputSizeFail1(self, mock):
        fromAngleListData(
            self.arrAziS[:-1],
            self.arrCoEleS,
            self.dataS,
            self.array.arrFreq,
            self.array.arrPos,
            60,
            30,
        )
        mock.assert_called_with(
            (
                "fromAngleListData: Input arrays"
                + " of sizes %d azi, %d ele, %d values dont match"
            )
            % (
                self.arrAziS[:-1].shape[0],
                self.arrCoEleS.shape[0],
                self.dataS.shape[0],
            )
        )

    @patch("logging.error")
    def test_inputSizeFail2(self, mock):
        fromAngleListData(
            self.arrAziS[:-1],
            self.arrCoEleS[:-1],
            self.dataS,
            self.array.arrFreq,
            self.array.arrPos,
            60,
            30,
        )
        mock.assert_called_with(
            (
                "fromAngleListData: Input arrays"
                + " of sizes %d azi, %d ele, %d values dont match"
            )
            % (
                self.arrAziS[:-1].shape[0],
                self.arrCoEleS[:-1].shape[0],
                self.dataS.shape[0],
            )
        )

    @patch("logging.error")
    def test_inputSizeFail3(self, mock):
        fromAngleListData(
            self.arrAziS,
            self.arrCoEleS,
            self.dataS,
            self.array.arrFreq,
            self.array.arrPos[:, :-1],
            60,
            30,
        )
        mock.assert_called_with(
            (
                "fromAngleListData:"
                + "Number of positions %d does not match provided data %d"
            )
            % (self.array.arrPos.shape[1] - 1, self.dataS.shape[3])
        )

    @patch("logging.error")
    def test_inputSizeFail4(self, mock):
        fromAngleListData(
            self.arrAziS,
            self.arrCoEleS,
            self.dataS,
            self.array.arrFreq[:-1],
            self.array.arrPos,
            60,
            30,
        )
        mock.assert_called_with(
            (
                "fromAngleListData:"
                + "Number of freqs %d does not match provided data %d"
            )
            % (self.array.arrFreq.shape[0] - 1, self.dataS.shape[1])
        )

    @patch("logging.error")
    def test_inputSizeFail5(self, mock):
        fromAngleListData(
            self.arrAziS,
            self.arrCoEleS,
            self.dataS,
            self.array.arrFreq,
            self.array.arrPos,
            -60,
            30,
        )
        mock.assert_called_with(
            "fromAngleListData: numAzi must be larger than 0."
        )

    @patch("logging.error")
    def test_inputSizeFail6(self, mock):
        fromAngleListData(
            self.arrAziS,
            self.arrCoEleS,
            self.dataS,
            self.array.arrFreq,
            self.array.arrPos,
            60,
            -30,
        )
        mock.assert_called_with(
            "fromAngleListData: numCoEle must be larger than 0."
        )


if __name__ == "__main__":
    unittest.main()
