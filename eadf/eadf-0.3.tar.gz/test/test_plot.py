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
from eadf.plot import plotBeamPattern2D
from eadf.plot import plotBeamPattern3D
from eadf.plot import plotCut2D
import unittest
from unittest.mock import patch


class TestPlotting(unittest.TestCase):
    @patch("matplotlib.pyplot.scatter")
    @patch("matplotlib.pyplot.show")
    def test_plotCut2D(self, show, scatter):
        plotCut2D(
            np.ones((20, 1, 2)),
            np.linspace(0, 2 * np.pi, 20),
            np.random.uniform(0, 1, (3, 2)),
        )
        self.assertTrue(show.called)
        self.assertTrue(scatter.called)

    @patch("logging.error")
    def test_plotCut2DFail1(self, mock):
        plotCut2D(
            np.ones((19, 1, 2)),
            np.linspace(0, 2 * np.pi, 20),
            np.random.uniform(0, 1, (3, 2)),
        )
        mock.assert_called_with(
            "plotCut2D:arrData.shape[0] %d does not fit arrAzi size %d"
            % (19, 20)
        )

    @patch("logging.error")
    def test_plotCut2DFail2(self, mock):
        plotCut2D(
            np.ones((20, 1, 3)),
            np.linspace(0, 2 * np.pi, 20),
            np.random.uniform(0, 1, (3, 2)),
        )
        mock.assert_called_with(
            "plotCut2D:Number of pos %d does not match data dimension %d"
            % (2, 3)
        )

    @patch("logging.error")
    def test_plotBeamPattern3DFail1(self, mock):
        plotBeamPattern3D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 20),
            np.linspace(0, np.pi, 20),
            np.random.uniform(0, 1, (3, 1)),
            4,
            4,
        )
        mock.assert_called_with(
            "plotBeamPattern3D:Num of CoEle and Azi %d,%d dont fit %d, %d"
            % (4, 4, 20, 1)
        )

    @patch("logging.error")
    def test_plotBeamPattern3DFail2(self, mock):
        plotBeamPattern3D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 19),
            np.linspace(0, np.pi, 20),
            np.random.uniform(0, 1, (3, 1)),
            5,
            4,
        )
        mock.assert_called_with(
            "plotBeamPattern3D:arrData.shape[0] %d doesnt fit arrAzi %d"
            % (20, 19)
        )

    @patch("logging.error")
    def test_plotBeamPattern3DFail3(self, mock):
        plotBeamPattern3D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 20),
            np.linspace(0, np.pi, 19),
            np.random.uniform(0, 1, (3, 1)),
            5,
            4,
        )
        mock.assert_called_with(
            "plotBeamPattern3D:arrData.shape[0] %d doesnt fit arrCoEle %d"
            % (20, 19)
        )

    @patch("logging.error")
    def test_plotBeamPattern3DFail4(self, mock):
        plotBeamPattern3D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 20),
            np.linspace(0, np.pi, 20),
            np.random.uniform(0, 1, (3, 2)),
            5,
            4,
        )
        mock.assert_called_with(
            "plotBeamPattern3D:Number of pos %d doesnt match data dim %d"
            % (2, 1)
        )

    @patch("matplotlib.pyplot.show")
    def test_plotBeamPattern3D(self, show):
        plotBeamPattern3D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 20),
            np.linspace(0, np.pi, 20),
            np.random.uniform(0, 1, (3, 1)),
            5,
            4,
        )
        self.assertTrue(show.called)

    @patch("matplotlib.pyplot.show")
    def test_plotBeamPattern2D(self, show):
        plotBeamPattern2D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 20),
            np.linspace(0, np.pi, 20),
            5,
            4,
        )
        self.assertTrue(show.called)

    @patch("logging.error")
    def test_plotBeamPattern2DFail1(self, mock):
        plotBeamPattern2D(
            np.ones((20, 1)),
            np.linspace(0, 2 * np.pi, 20),
            np.linspace(0, np.pi, 20),
            4,
            4,
        )
        mock.assert_called_with(
            "plotBeamPattern2D:Num of CoEle and Azi %d,%d dont fit data %d,%d"
            % (4, 4, 20, 1)
        )
