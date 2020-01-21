#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 28 08:32:24 2018

@author: mcsoini
"""

import numpy as np
import pandas as pd

def get_example_data_100():

    # % Example charging/discharging profiles
    x = np.arange(100)

    def add_peaks(peaks, threshold=0.1):
        cd = np.array([0.] * len(x))
        for amp, pos, area in peaks:
            sigma = area / (amp * np.sqrt(2 * np.pi))
            cd += amp * np.exp(-1/2 * ((x - pos)/sigma)**2)
        # simplify
        cd[np.abs(cd) < threshold] = 0
        # calculate soc
        soc = np.cumsum(cd)
        # make sure soc is zero at the beginning and the end
        soc[(soc == soc[-1]) | (soc == soc[0])] = 0
        # recalculate cd
        cd = np.concatenate([np.array([0.]), np.diff(soc)])
        return cd, soc

    peaks_left = [(0.8, 23, 7), (-0.8, 29, 7),
                  (0.5, 5, 3), (-0.4, 17, 3),
                  (0.7, 38, 3), (-0.6, 40, 3)]
    cd_l, soc_l = add_peaks(peaks_left)

    peaks_right_1 = [(+1, 53, 5), (-1, 60, 5)]
    cd_r1, soc_r1 = add_peaks(peaks_right_1)

    peaks_right_2 = [(+0.8, 68, 2), (+0.8, 75, 1), (-0.8, 95, 3)]
    cd_r2, soc_r2 = add_peaks(peaks_right_2)

    cd = cd_l + cd_r1 + cd_r2

    c = cd.copy()
    c[c < 0] = 0
    d = cd.copy()
    d[d > 0] = 0

    df = pd.DataFrame(np.array([x, c, -d]).T,
                      columns=['t', 'chg', 'dch'])

    return df
