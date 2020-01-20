#
# Copyright (C) 2014-2019 GEM Foundation
#
# OpenQuake is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenQuake is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with OpenQuake. If not, see <http://www.gnu.org/licenses/>.


"""
:module:`openquake.hazardlib.gsim.can15.western` implements
:class:`WesternCan15Mid`, :class:`WesternCan15Low`, :class:`WesternCan15Upp`
"""

import copy
import numpy as np
from openquake.hazardlib.gsim.can15.utils import \
    get_equivalent_distances_west
from openquake.hazardlib.gsim.boore_atkinson_2011 import BooreAtkinson2011
from openquake.hazardlib.const import StdDev


def get_sigma(imt):
    """
    Return the value of the total sigma

    :param float imt:
        An :class:`openquake.hazardlib.imt.IMT` instance
    :returns:
        A float representing the total sigma value
    """
    if imt.period < 0.2:
        return np.log(10**0.23)
    elif imt.period > 1.0:
        return np.log(10**0.27)
    else:
        return np.log(10**(0.23 + (imt.period - 0.2)/0.8 * 0.04))


class WesternCan15Mid(BooreAtkinson2011):
    """
    Implements the Boore and Atkinson (2008) with adjustments proposed by
    Boore and Atkinson (2011) and the modifications introduced for the
    calculation of hazard for the fifth generation of Canada's hazard maps,
    released in 2015.
    """

    #: GMPE not tested against independent implementation so raise
    #: not verified warning
    non_verified = True

    #: Shear-wave velocity for reference soil conditions in [m s-1]
    DEFINED_FOR_REFERENCE_VELOCITY = 760.

    #: Standard deviation types supported
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = set([StdDev.TOTAL])

    #: Required distance is only repi since rrup and rjb are obtained from repi
    REQUIRES_DISTANCES = set(('repi',))

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        """ """
        # distances
        distsl = copy.copy(dists)
        distsl.rjb, distsl.rrup = \
            get_equivalent_distances_west(rup.mag, dists.repi)
        # get original values
        mean, stddevs = super().get_mean_and_stddevs(sites, rup, distsl, imt,
                                                     stddev_types)
        stds = [np.ones(len(distsl.rjb))*get_sigma(imt)]
        return mean, stds


class WesternCan15Low(WesternCan15Mid):

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        # distances
        distsl = copy.copy(dists)
        distsl.rjb, distsl.rrup = \
            get_equivalent_distances_west(rup.mag, dists.repi)
        # get original values
        mean, _ = super().get_mean_and_stddevs(sites, rup, distsl, imt,
                                               stddev_types)
        # adjust mean values using the reccomended delta (see Atkinson and
        # Adams, 2013)
        tmp = 0.1+0.0007*distsl.rjb
        tmp = np.vstack((tmp, np.ones_like(tmp)*0.3))
        delta = np.log(10.**(np.amin(tmp, axis=0)))
        mean_adj = mean - delta
        stddevs = [np.ones(len(distsl.rjb))*get_sigma(imt)]
        return mean_adj, stddevs


class WesternCan15Upp(WesternCan15Mid):

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        """ """
        # distances
        distsl = copy.copy(dists)
        distsl.rjb, distsl.rrup = \
            get_equivalent_distances_west(rup.mag, dists.repi)
        # get original values
        mean, _ = super().get_mean_and_stddevs(sites, rup, distsl, imt,
                                               stddev_types)
        # Adjust mean values using the reccomended delta (see Atkinson and
        # Adams, 2013)
        tmp = 0.1+0.0007*distsl.rjb
        tmp = np.vstack((tmp, np.ones_like(tmp)*0.3))
        delta = np.log(10.**(np.amin(tmp, axis=0)))
        mean_adj = mean + delta
        stddevs = [np.ones(len(distsl.rjb))*get_sigma(imt)]
        return mean_adj, stddevs
