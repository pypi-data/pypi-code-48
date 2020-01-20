# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 softtabstop=4
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
Module exports :class:`AmeriEtAl2017Rjb`,
               :class:`AmeriEtAl2017Repi`,
               :class:`AmeriEtAl2017RjbStressDrop`,
               :class:`AmeriEtAl2017RepiStressDrop`
"""
import numpy as np
g = 9.81  # According to G. Ameri, pers. communication (May 20th, 2019)
from openquake.hazardlib.gsim.base import GMPE, CoeffsTable
from openquake.hazardlib import const
from openquake.hazardlib.imt import PGA, SA


class AmeriEtAl2017Rjb(GMPE):
    """
    Implements the Ameri et al (2017) GMPE for the case where Joyner-Boore
    distance is used. Standard deviation uses the heteroscedastic formulation
    given in eqn. 11. (for periods T<=1 s.)
    
    Reference:
    Ameri, G., Drouet, S., Traversa, P., Bindi, D., Cotton, F., (2017),
    Toward an empirical ground motion prediction equation for France: 
    accounting for regional differences in the source stress parameter, 
    Bull. Earthquake Eng., 15: 4681-4717.
    """
    #: Supported tectonic region type is 'active shallow crust'
    DEFINED_FOR_TECTONIC_REGION_TYPE = const.TRT.ACTIVE_SHALLOW_CRUST

    #: Set of :mod:`intensity measure types <openquake.hazardlib.imt>`
    #: this GSIM can calculate. A set should contain classes from module
    #: :mod:`openquake.hazardlib.imt`.
    DEFINED_FOR_INTENSITY_MEASURE_TYPES = set([
        PGA,
        SA
    ])

    #: Supported intensity measure component is the geometric mean of two
    #: horizontal components
    DEFINED_FOR_INTENSITY_MEASURE_COMPONENT = const.IMC.AVERAGE_HORIZONTAL

    #: Supported standard deviation types are inter-event, intra-event
    #: and total
    DEFINED_FOR_STANDARD_DEVIATION_TYPES = set([
        const.StdDev.TOTAL,
        const.StdDev.INTER_EVENT,
        const.StdDev.INTRA_EVENT
    ])

    #: Required site parameter is only Vs30
    REQUIRES_SITES_PARAMETERS = set(('vs30', ))

    #: Required rupture parameters are magnitude and rake (eq. 1).
    REQUIRES_RUPTURE_PARAMETERS = set(('rake', 'mag'))

    #: Required distance measure is Rjb (eq. 1).
    REQUIRES_DISTANCES = set(('rjb', ))

    def __init__(self, adjustment_factor=1.0):
        super().__init__()
        self.adjustment_factor = np.log(adjustment_factor)

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        """
        See :meth:`superclass method
        <.base.GroundShakingIntensityModel.get_mean_and_stddevs>`
        for spec of input and result values.
        """
        # extracting dictionary of coefficients specific to required
        # intensity measure type.

        C = self.COEFFS[imt]
        C_SIGMA = self.COEFFS_SIGMA[imt]
        imean = self._get_mean(C, rup, dists, sites)
        # Convert mean to ln(SA) with SA in units of g:
        mean = np.log((10.0 ** (imean - 2.0)) / g)

        istddevs = self._get_stddevs(C_SIGMA, stddev_types, len(sites.vs30), rup.mag)
        stddevs = np.log(10.0 ** np.array(istddevs))
        return mean + self.adjustment_factor, stddevs

    def _get_mean(self, C, rup, dists, sites):
        """
        Returns the mean ground motion (i.e. log10(ground motion in cm/s^2) )
        """
        return (C["a"] + 
                self._get_distance_scaling_term(C, dists.rjb, rup.mag) +
                self._get_magnitude_scaling_term(C, rup.mag) +
                self._get_site_amplification_term(C, sites.vs30) +
                self._get_style_of_faulting_term(C, rup.rake))

    def _get_magnitude_scaling_term(self, C, mag):
        """
        Returns the magnitude scaling term of the GMPE described in
        equation 3
        """
        dmag = mag - self.CONSTS["Mh"]
        if mag <= self.CONSTS["Mh"]:
            return C["b1"] * dmag + C["b2"] * (dmag ** 2.0)
        else:
            return C["b3"]* dmag

    def _get_distance_scaling_term(self, C, rval, mag):
        """
        Returns the distance scaling term of the GMPE described in equation 2
        """
        r_adj = np.sqrt((rval ** 2.0) + (C["h"] ** 2.0))
        return (
            (C["c1"] + C["c2"] * (mag - self.CONSTS["Mref"])) *
            np.log10(r_adj / self.CONSTS["Rref"]))

    def _get_style_of_faulting_term(self, C, rake):
        """
        Returns the style-of-faulting term of the GMPE described in equation 4
        Fault type (Strike-slip, Normal, Thrust/reverse) is
        derived from rake angle.
        Rakes angles within 30 of horizontal are strike-slip,
        angles from 30 to 150 are reverse, and angles from
        -30 to -150 are normal.
        Note that the 'Unspecified' case is not considered in this class
        as rake is required as an input variable
        """
        SS, NS, RS = 0.0, 0.0, 0.0
        if np.abs(rake) <= 30.0 or (180.0 - np.abs(rake)) <= 30.0:
            # strike-slip
            SS = 1.0
        elif rake > 30.0 and rake < 150.0:
            # reverse
            RS = 1.0
        else:
            # normal
            NS = 1.0
        return (C["f1"] * NS) + (C["f2"] * RS) + (C["f3"] * SS)

    def _get_site_amplification_term(self, C, vs30):
        """
        Returns the site amplification given Eurocode 8 site classification
        """
        f_s = np.zeros_like(vs30)
        # Site class A
        idx = vs30 >= 800.0
        f_s[idx] = C["e1"]
        # Site class B
        idx = np.logical_and(vs30 < 800.0, vs30 >= 360.0)
        f_s[idx] = C["e2"]
        # Site Class C
        idx = np.logical_and(vs30 < 360.0, vs30 >= 180.0)
        f_s[idx] = C["e3"]
        # Site Class D
        idx = vs30 < 180.0
        f_s[idx] = C["e4"]
        return f_s

    def _get_stress_term(self, C, mag, norm_stress_drop):
        """
        Returns the stress parameter-dependent term, based on Yenier and Atkinson (2015)
        """
        if norm_stress_drop<=1:
            e = C['s0'] + C['s1'] * mag + C['s2'] * (mag**2) + \
                C['s3'] * (mag**3) + C['s4'] * (mag**4)
        else:
            e = C['s5'] + C['s6'] * mag + C['s7'] * (mag**2) + \
                C['s8'] * (mag**3) + C['s9'] * (mag**4)
        return e * np.log10( norm_stress_drop )

    def _get_stddevs(self, C_SIGMA, stddev_types, num_sites, mag):
        """
        Return standard deviations
        """
        tau = self._compute_between_events_std(C_SIGMA, mag)
        phi = self._compute_within_event_std(C_SIGMA)
        sigma = np.sqrt( tau**2 + phi**2 )
        stddevs = []
        for stddev_type in stddev_types:
            assert stddev_type in self.DEFINED_FOR_STANDARD_DEVIATION_TYPES
            if stddev_type == const.StdDev.TOTAL:
                stddevs.append(sigma + np.zeros(num_sites))
            elif stddev_type == const.StdDev.INTRA_EVENT:
                stddevs.append(phi + np.zeros(num_sites))
            elif stddev_type == const.StdDev.INTER_EVENT:
                stddevs.append(tau + np.zeros(num_sites))
        return stddevs

    def _compute_between_events_std(self, C_SIGMA, mag):
        """
        Return between-events standard deviation term. Expression is provided:
        - according to eqn. 11 if model is heteroscedastic (mag parameter is not None);
        - or using a constant term if model is homoscedastic (mag parameter is None).
        """
        if mag is None:
            # Homoscedastic model:
            tau = C_SIGMA['tau']
        else:
            # Heteroscedastic model:
            if mag<=4.0:
                tau = C_SIGMA['tau1']
            elif mag>=5:
                tau = C_SIGMA['tau2']
            else:
                tau = C_SIGMA['tau1'] + (C_SIGMA['tau2']-C_SIGMA['tau1'])*(mag-4.0)
        return tau

    def _compute_within_event_std(self, C_SIGMA):
        """
        Return within-event standard deviation
        """
        return C_SIGMA['phi']


    #: Coefficients from Table "10518_2017_171_MOESM2_ESM.xlsx" in electronic supplementary material:
    COEFFS = CoeffsTable(sa_damping=5, table="""
    imt           a              c1             c2             h              b1             b2             b3             e1             e2             e3             e4             f1             f2             f3                      
    pga        3.57937        -1.4864       0.231465        6.65758     -0.0240888     -0.0631411              0              0       0.167762       0.249286       0.223014     -0.0382253       0.013243              0           
    0.01         3.5972       -1.49427       0.234091        6.79747     -0.0222199     -0.0600105              0              0       0.160126        0.24238       0.218539     -0.0347956      0.0177128              0          
    0.02        3.63617       -1.50665       0.234304        6.60957    -0.00818666     -0.0545415              0              0       0.149801       0.231588       0.212933     -0.0317685      0.0190783              0          
    0.03        3.69185       -1.54706       0.253029        6.83552     -0.0212604     -0.0434654              0              0        0.13237       0.210271       0.193703     -0.0248664       0.037243              0          
    0.04        3.74843       -1.57163       0.254487        6.84157      -0.023062     -0.0368002              0              0        0.13248       0.198745       0.160215     -0.0186509      0.0384935              0          
    0.05         3.8254       -1.59374       0.244296        6.97997     -0.0265193      -0.038679              0              0       0.135848       0.191212       0.142625     -0.0172171      0.0385044              0          
   0.075        4.02576       -1.62183       0.195296        7.29363    -0.00942327     -0.0570317              0              0       0.163595       0.202134       0.142641     -0.0238157      0.0230891              0          
     0.1        4.12894       -1.62321       0.163216        7.62694    -0.00570805     -0.0775024              0              0       0.200864       0.232295       0.173399     -0.0222679      0.0115192              0          
    0.15        4.14147       -1.55679       0.137411        7.59936    -0.00140059      -0.103665              0              0       0.230128       0.261189       0.229835     -0.0312945     -0.0134991              0          
     0.2        4.03038        -1.4505       0.122409        6.71189      0.0251505      -0.117975              0              0       0.222592       0.282414       0.254405     -0.0375677     -0.0132365              0          
    0.26        3.89003       -1.35644       0.112647        6.06462       0.058444       -0.12719              0              0        0.22463       0.318629       0.280155     -0.0438534     -0.0228273              0          
     0.3        3.79547       -1.29433       0.105082        5.40797      0.0826731      -0.132525              0              0        0.21436       0.330943       0.293392      -0.052228     -0.0249144              0          
    0.36        3.65477       -1.21655       0.102617         4.6578       0.123373       -0.13208              0              0       0.218341       0.357137       0.336488     -0.0545282     -0.0369904              0          
     0.4        3.57828       -1.18611       0.105263        4.45728       0.136293       -0.13249              0              0       0.225607       0.373643        0.36356     -0.0575379     -0.0445194              0          
    0.46        3.50977       -1.15887       0.108003        4.24293       0.159692      -0.131675              0              0       0.225533       0.392129       0.408201      -0.068798     -0.0588553              0          
     0.5         3.4641       -1.13335       0.106464        3.92775       0.184071      -0.130586              0              0       0.223114       0.401878       0.437158     -0.0755826     -0.0659854              0          
     0.6        3.35334       -1.09668       0.110251        3.67158       0.215812      -0.129838              0              0       0.221907       0.414504       0.504533      -0.075854      -0.075577              0          
     0.7        3.24798       -1.06758       0.110992        3.36202         0.2287      -0.132434              0              0       0.217418       0.421098       0.561574     -0.0780016     -0.0913044              0          
     0.8        3.13832       -1.03218       0.118672        3.15358       0.247122       -0.13043              0              0       0.207333       0.424843       0.594304     -0.0776178      -0.100387              0          
     0.9        3.07595       -1.00932       0.116383        3.16122       0.277383      -0.130108              0              0        0.20214       0.432693       0.633541     -0.0793058      -0.106253              0          
     1.0        3.01481      -0.990675       0.114962        3.04105       0.313627      -0.125759              0              0       0.203179       0.434754        0.64753     -0.0734174       -0.10704              0          
     1.3         2.8491      -0.954153       0.131841        3.03741       0.362253      -0.118367              0              0       0.189662       0.417724       0.679776     -0.0769343      -0.111787              0          
     1.5        2.79803      -0.949676       0.128459        2.97213       0.417589      -0.111117              0              0       0.190107       0.414214       0.719585     -0.0766813      -0.101168              0          
     1.8        2.77959      -0.966699       0.125038        3.65762       0.480496      -0.102423              0              0       0.176816        0.39028       0.674517     -0.0860793      -0.103835              0          
     2.0        2.75262      -0.973361       0.124103        3.78649       0.505881      -0.100896              0              0       0.169768       0.385618         0.6598     -0.0959682        -0.1124              0          
     2.6         2.5907      -0.964381       0.143781        3.87901       0.541547     -0.0930562              0              0       0.140212        0.33995       0.604624      -0.081575      -0.104082              0          
     3.0        2.50167      -0.950629       0.164955        4.11679       0.599563     -0.0673578              0              0       0.124967       0.321712       0.607734     -0.0900985      -0.114396              0          
    """)

    # Coefficients from Table "10518_2017_171_MOESM3_ESM.xlsx" in electronic supplementary material:
    # NB: Coefficients from the original table have been modified so as to account for the authors' 
    #     advice in the article (p.4707, "we recommend the heteroscedastic model for T<=1 s only, 
    #     and the homoscedastic model for longer periods".
    #     Accordingly, values for TAU1 and TAU2 have been edited to match TAU values for the following
    #     periods: 1.3 s., 1.5 s., 1.8 s., 2.0 s., 2.6 s., 3.0 s.
    COEFFS_SIGMA = CoeffsTable(sa_damping=5, table="""
        imt             tau       tau1       tau2       phi        
        pga         0.170688   0.299730   0.177908   0.303741
       0.01         0.171851   0.299730   0.177908   0.305812
       0.02         0.173021   0.311915   0.186848   0.307893
       0.03         0.179043   0.305421   0.189678   0.318609
       0.04         0.174265   0.328821   0.194362   0.328130
       0.05         0.176014   0.339281   0.199864   0.331423
      0.075         0.184290   0.331247   0.214309   0.327946
        0.1         0.190709   0.309358   0.210499   0.321737
       0.15         0.186913   0.292712   0.199181   0.315332
        0.2         0.187804   0.272432   0.192531   0.301156
       0.26         0.174769   0.241235   0.179662   0.294844
        0.3         0.173561   0.237312   0.171560   0.292807
       0.36         0.174919   0.216497   0.167742   0.295097
        0.4         0.168289   0.209183   0.161301   0.299473
       0.46         0.169701   0.204619   0.162074   0.301986
        0.5         0.169913   0.203503   0.162521   0.302362
        0.6         0.169173   0.200595   0.162803   0.301045
        0.7         0.171074   0.202465   0.165952   0.304429
        0.8         0.170979   0.198534   0.157879   0.304259
        0.9         0.168764   0.187191   0.155639   0.300318
        1.0         0.176172   0.184987   0.154404   0.297212
        1.3         0.183978   0.183978   0.183978   0.295022
        1.5         0.184155   0.184155   0.184155   0.295306
        1.8         0.184885   0.184885   0.184885   0.296476
        2.0         0.185435   0.185435   0.185435   0.297357
        2.6         0.210376   0.210376   0.210376   0.293109
        3.0         0.212859   0.212859   0.212859   0.283812
    """)

    # Coefficients from Table "10518_2017_171_MOESM4_ESM.xlsx" in electronic supplementary material
    # (see also Yenier and Atkinson, 2015):
    COEFFS_STRESS = CoeffsTable(sa_damping=5, table="""
    imt      s0                        s1                        s2                        s3                        s4                        s5                        s6                        s7                        s8                        s9                        
    pga     -2.132000000000000000      1.937000000000000000     -0.504000000000000000      0.058240000000000000     -0.002498000000000000     -1.444000000000000000      1.235000000000000000     -0.285100000000000000      0.030210000000000000     -0.001217000000000000
   0.01     -2.048000000000000000      1.881000000000000000     -0.490100000000000000      0.056680000000000000     -0.002433000000000000     -1.437000000000000000      1.242000000000000000     -0.289200000000000000      0.030880000000000000     -0.001252000000000000
   0.02     -1.160000000000000000      1.274000000000000000     -0.334400000000000000      0.039110000000000000     -0.001700000000000000     -1.272000000000000000      1.254000000000000000     -0.317100000000000000      0.036240000000000000     -0.001550000000000000
   0.03     -1.056000000000000000      1.205000000000000000     -0.313200000000000000      0.036150000000000000     -0.001550000000000000     -2.243000000000000000      1.981000000000000000     -0.508600000000000000      0.057820000000000000     -0.002439000000000000
   0.04     -0.857100000000000000      1.044000000000000000     -0.267700000000000000      0.030820000000000000     -0.001328000000000000     -3.310000000000000000      2.663000000000000000     -0.668300000000000000      0.074150000000000000     -0.003056000000000000
   0.05     -0.962800000000000000      0.982600000000000000     -0.215600000000000000      0.020800000000000000     -0.000742300000000000     -4.228000000000000000      3.293000000000000000     -0.831600000000000000      0.093030000000000000     -0.003873000000000000
  0.075     -3.307093622752820000      2.715618872036960000     -0.691461347788890000      0.077930164008379800     -0.003265156851659290     -3.391720419721760000      2.384390298763130000     -0.525460084931779000      0.051464187772421400     -0.001885243731635890
   0.10     -4.051000000000000000      3.100000000000000000     -0.762500000000000000      0.083280000000000000     -0.003393000000000000     -2.452000000000000000      1.569000000000000000     -0.289000000000000000      0.023000000000000000     -0.000657300000000000
   0.15     -4.135496790484950000      2.990175665924260000     -0.703560572208682000      0.074081088832166700     -0.002926336129704660     -0.559855506733657000     -0.053291402105396500      0.180588831258940000     -0.033835675561780300      0.001817879129878780
   0.20     -2.707000000000000000      1.729000000000000000     -0.330200000000000000      0.028160000000000000     -0.000906400000000000      0.819700000000000000     -1.083000000000000000      0.439500000000000000     -0.061050000000000000      0.002846000000000000
   0.26     -1.505285261389930000      0.778534841420447000     -0.076457065704366200     -0.000269726890490286      0.000248305753738586      1.899210650769040000     -1.836817196760830000      0.618619194004931000     -0.078935922164824500      0.003491574884857080
   0.30     -0.318200000000000000     -0.138600000000000000      0.170400000000000000     -0.028500000000000000      0.001421000000000000      2.245000000000000000     -2.003000000000000000      0.632600000000000000     -0.076990000000000000      0.003268000000000000
   0.36      1.111764905130550000     -1.191881353033970000      0.439960248224610000     -0.057764942347499700      0.002573205245872980      2.596970663273000000     -2.161763564108410000      0.643269347166781000     -0.074790329176234400      0.003050023155703400
   0.40      2.018000000000000000     -1.857000000000000000      0.611700000000000000     -0.076740000000000000      0.003341000000000000      2.422000000000000000     -1.938000000000000000      0.555800000000000000     -0.061740000000000000      0.002390000000000000
   0.46      3.370459349501280000     -2.867857822677980000      0.881282613938582000     -0.107753617606812000      0.004656357005019520      1.511700286086790000     -1.063201044297120000      0.263446359042810000     -0.021599838071486900      0.000449893309699056
   0.50      3.956000000000000000     -3.288000000000000000      0.988500000000000000     -0.119600000000000000      0.005142000000000000      0.855500000000000000     -0.452800000000000000      0.064590000000000000      0.005220000000000000     -0.000829900000000000
   0.60      4.005249108906740000     -3.183158831926270000      0.917619630870284000     -0.106718967852185000      0.004415895819937990     -0.245407670497777000      0.555351425397322000     -0.256909575045555000      0.047551190466675300     -0.002799950197340630
   0.70      3.209976852768910000     -2.406186937090780000      0.654683779233643000     -0.070222093434176500      0.002629549156714740     -1.091578741397200000      1.292319501723110000     -0.479373955359707000      0.075037674525423100     -0.003993830592681950
   0.80      2.404000000000000000     -1.652000000000000000      0.408800000000000000     -0.037100000000000000      0.001051000000000000     -2.124000000000000000      2.152000000000000000     -0.730100000000000000      0.105300000000000000     -0.005287000000000000
   0.90      1.809528912677510000     -1.104457948914730000      0.235192596243833000     -0.014593092486076200      0.000026650903092806     -3.410479563877170000      3.201765159152890000     -1.033659203023420000      0.142312111204227000     -0.006905803814287950
   1.00      1.066000000000000000     -0.455200000000000000      0.037390000000000000      0.010330000000000000     -0.001084000000000000     -4.473000000000000000      4.051000000000000000     -1.274000000000000000      0.171000000000000000     -0.008137000000000000
   1.30     -2.508000000000000000      2.523000000000000000     -0.844600000000000000      0.120500000000000000     -0.006024000000000000     -5.494000000000000000      4.766000000000000000     -1.439000000000000000      0.184900000000000000     -0.008458000000000000
   1.50     -4.562591209586210000      4.184178885193690000     -1.321626951817460000      0.178297179632034000     -0.008536305641724080     -5.752786034123840000      4.904176324860710000     -1.453760278582560000      0.183165745788638000     -0.008216131058600520
   1.80     -6.066252631749060000      5.345315499812140000     -1.635798607735410000      0.213421543697430000     -0.009917991992558870     -6.081700433391410000      5.092342470146320000     -1.481158779327170000      0.182998865017356000     -0.008050251934664040
    2.0     -6.642000000000000000      5.767000000000000000     -1.742000000000000000      0.224100000000000000     -0.010280000000000000     -6.010000000000000000      4.985000000000000000     -1.433000000000000000      0.174800000000000000     -0.007587000000000000
    2.6     -8.161077047405510000      6.880595832041620000     -2.024661773244400000      0.253463377249699000     -0.011347702706097400     -4.707867446814010000      3.789164702352790000     -1.037841219533240000      0.119381787710041000     -0.004831972404074730
    3.0     -7.980000000000000000      6.643000000000000000     -1.924000000000000000      0.236600000000000000     -0.010390000000000000     -4.180000000000000000      3.317000000000000000     -0.886200000000000000      0.098880000000000000     -0.003853000000000000
    """)

    CONSTS = {"Mref": 5.5,
              "Mh": 6.75,
              "Rref": 1.0}


class AmeriEtAl2017RjbStressDrop(AmeriEtAl2017Rjb):
    """
    Implements the Ameri et al (2017) GMPE for the case where Joyner-Boore
    distance is used, and the stress parameter is specified in the Ground-motion
    logic-tree.
    Example specification of the normalizaed stress parameter:
    <uncertaintyModel>
        [AmeriEtAl2017RjbStressDrop]
        norm_stress_drop = 0.3
    </uncertaintyModel>
    The stress parameter is normalized, according to STRESS_DROP/REF_STRESS_DROP,
    where REF_STRESS_DROP varies regionally. The authors used the following values 
    for reference regional stress estimates: 1 bar for the Swtzerland (Swiss Alps
    +Foreland), 10 bars for the French Alps + Rhine Graben, and 100 bars for the 
    Pyrenees events. In this case, the standard deviation implements a homoscedastic
    formulation.
    
    Reference:
    Ameri, G., Drouet, S., Traversa, P., Bindi, D., Cotton, F., (2017),
    Toward an empirical ground motion prediction equation for France: 
    accounting for regional differences in the source stress parameter, 
    Bull. Earthquake Eng., 15: 4681-4717.
    """
    #: Required rupture parameters are magnitude and rake (eq. 1).
    REQUIRES_RUPTURE_PARAMETERS = set(('rake', 'mag'))

    def __init__(self, norm_stress_drop, adjustment_factor=1.0):
        super().__init__(adjustment_factor=adjustment_factor)
        self.norm_stress_drop = norm_stress_drop

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        """
        See :meth:`superclass method
        <.base.GroundShakingIntensityModel.get_mean_and_stddevs>`
        for spec of input and result values.
        """
        # extracting dictionary of coefficients specific to required
        # intensity measure type.

        C = self.COEFFS[imt]
        C_SIGMA = self.COEFFS_SIGMA[imt]
        C_STRESS = self.COEFFS_STRESS[imt]
        imean = self._get_mean(C, C_STRESS, rup, dists, sites)
        # Convert mean to ln(SA) with SA in units of g:
        mean = np.log((10.0 ** (imean - 2.0)) / g)

        istddevs = self._get_stddevs(C_SIGMA, stddev_types, len(sites.vs30), None)
        stddevs = np.log(10.0 ** np.array(istddevs))
        return mean + self.adjustment_factor, stddevs

    def _get_mean(self, C, C_STRESS, rup, dists, sites):
        """
        Returns the mean ground motion
        """
        return (C["a"] + 
                self._get_magnitude_scaling_term(C, rup.mag) +
                self._get_distance_scaling_term(C, dists.rjb, rup.mag) +
                self._get_style_of_faulting_term(C, rup.rake) +
                self._get_site_amplification_term(C, sites.vs30) +
                self._get_stress_term(C_STRESS, rup.mag, self.norm_stress_drop))
 

class AmeriEtAl2017Repi(AmeriEtAl2017Rjb):
    """
    Implements the Ameri et al (2017) GMPE for the case where epicentral
    distance is used. Standard deviation uses the heteroscedastic formulation
    given in eqn. 11. (for periods T<=1 s.)

    Reference:
    Ameri, G., Drouet, S., Traversa, P., Bindi, D., Cotton, F., (2017),
    Toward an empirical ground motion prediction equation for France: 
    accounting for regional differences in the source stress parameter, 
    Bull. Earthquake Eng., 15: 4681-4717.
    """

    #: Required distance measure is Repi (eq. 1).
    REQUIRES_DISTANCES = set(('repi', ))

    def _get_mean(self, C, rup, dists, sites):
        """
        Returns the mean ground motion
        """
        return (C["a"] + 
                self._get_magnitude_scaling_term(C, rup.mag) +
                self._get_distance_scaling_term(C, dists.repi, rup.mag) +
                self._get_style_of_faulting_term(C, rup.rake) +
                self._get_site_amplification_term(C, sites.vs30))
    
    #: Coefficients from Table "10518_2017_171_MOESM1_ESM.xlsx" in electronic supplementary material:
    COEFFS = CoeffsTable(sa_damping=5, table="""
        imt           a              c1             c2             h              b1             b2             b3             e1             e2             e3             e4             f1             f2             f3                 
        pga        3.90119        -1.5472       0.203801        6.78654       0.157748     -0.0375241              0              0       0.183962       0.265793       0.223751     -0.0467904      0.0184746              0    
       0.01        3.91834       -1.55513       0.206695        6.93871       0.158768     -0.0344853              0              0       0.176314       0.258883       0.219586     -0.0433188      0.0229539              0    
       0.02        3.96778       -1.56944       0.204904        6.71767       0.179572     -0.0283156              0              0       0.166393       0.248523       0.216466     -0.0404006      0.0245037              0    
       0.03        4.03457       -1.61309       0.221786        6.97123       0.170789     -0.0170738              0              0         0.1495        0.22776       0.198027      -0.033472      0.0429289              0    
       0.04        4.09161       -1.63695       0.223878        6.93988       0.170856    -0.00977618              0              0       0.149521       0.216085       0.161634     -0.0274375      0.0441535              0    
       0.05        4.16164       -1.65202       0.213028        6.87221       0.173549     -0.0106632              0              0       0.153353       0.208313       0.142202     -0.0260106      0.0440531              0    
       0.075        4.33841        -1.6683       0.169004        7.00747       0.189381     -0.0275671              0              0       0.180887       0.218339       0.140321     -0.0334549      0.0279034              0   1
       0.10        4.42216       -1.66545       0.142599        7.42062       0.181596     -0.0484681              0              0       0.217184       0.248079       0.169717     -0.0322814      0.0161202              0    
       0.15        4.41412       -1.59603       0.121696        7.46484       0.172235      -0.075683              0              0       0.245926       0.275714       0.226713     -0.0406154    -0.00923057              0    
       0.20        4.29143       -1.48937       0.109037        6.66175       0.188457     -0.0912278              0              0       0.237868       0.296127       0.251076     -0.0473502    -0.00965523              0    
       0.26        4.15414        -1.3971      0.0981806        6.01355       0.222792      -0.100492              0              0       0.240346       0.331854       0.276914     -0.0529457     -0.0200077              0    
       0.30        4.06715       -1.33781      0.0881106        5.40572       0.249494      -0.106148              0              0       0.229999       0.344676       0.291959      -0.061157     -0.0217789              0    
       0.36        3.93473       -1.26446       0.082679        4.76415       0.290781      -0.106547              0              0       0.234552       0.371843       0.336232     -0.0634606     -0.0336804              0    
       0.40        3.86858        -1.2376      0.0824992        4.59994       0.307618      -0.107085              0              0       0.242295       0.388648       0.362821     -0.0660934     -0.0413226              0    
       0.46        3.80262        -1.2128        0.08412        4.46018       0.329334      -0.106975              0              0       0.241844       0.407015       0.405404     -0.0767804     -0.0551733              0    
       0.50        3.76231       -1.18977      0.0810918        4.20281       0.354457      -0.106229              0              0       0.239285       0.416952       0.433658     -0.0835497     -0.0619977              0    
       0.60        3.65478       -1.15523      0.0833905        4.00398       0.385689      -0.106057              0              0       0.237641       0.429496       0.500227     -0.0833572     -0.0718527              0    
       0.70        3.55408       -1.13019      0.0840393        3.85672       0.396746      -0.108988              0              0       0.232891       0.436872       0.559456     -0.0853279     -0.0872709              0    
       0.80        3.44534       -1.09309      0.0883406         3.4791       0.419463       -0.10718              0              0       0.223144        0.44086       0.594032     -0.0851173     -0.0969812              0    
       0.90        3.37653       -1.06841      0.0860723        3.48856       0.446457      -0.107469              0              0       0.217031       0.448439       0.634135     -0.0872213      -0.103167              0    
       1.0        3.31044       -1.04917       0.085526        3.38282       0.479407      -0.103463              0              0       0.217976       0.449865          0.647     -0.0811993      -0.103835              0     
       1.3        3.13628       -1.01108       0.101962        3.39674       0.523028     -0.0971368              0              0       0.204172       0.433443       0.680322      -0.085345      -0.108176              0     
       1.5        3.08483       -1.00615      0.0983393        3.32168       0.580112     -0.0894907              0              0       0.205563       0.430942       0.719757      -0.085572      -0.095703              0     
       1.8        3.05563       -1.01592      0.0933633         3.5879        0.64878     -0.0794491              0              0       0.191903        0.40723       0.673431     -0.0933542     -0.0975485              0     
       2.0        3.03188       -1.02463      0.0921217        3.80958       0.673389     -0.0781992              0              0       0.184302        0.40322       0.658312      -0.103371      -0.105662              0     
       2.6        2.87034       -1.01797       0.111257        4.12602       0.708014     -0.0696517              0              0       0.155283       0.359284       0.603672     -0.0906715     -0.0973401              0     
       3.0        2.77941       -1.00223       0.130875        4.44146       0.773886     -0.0405902              0              0       0.140958       0.341313       0.606863     -0.0982915      -0.108276              0     
    """)

    # Coefficients from Table "10518_2017_171_MOESM3_ESM.xlsx" in electronic supplementary material:
    # NB: Coefficients from the original table have been modified so as to account for the authors' 
    #     advice in the article (p.4707, "we recommend the heteroscedastic model for T<=1 s only, 
    #     and the homoscedastic model for longer periods".
    #     Accordingly, values for TAU1 and TAU2 have been edited to match TAU values for the following
    #     periods: 1.3 s., 1.5 s., 1.8 s., 2.0 s., 2.6 s., 3.0 s.
    COEFFS_SIGMA = CoeffsTable(sa_damping=5, table="""
        imt             tau       tau1       tau2          phi            
        pga        0.171510   0.311636   0.180874     0.305205
       0.01        0.172616   0.311636   0.180874     0.307173
       0.02        0.173732   0.311987   0.182078     0.309158
       0.03        0.179536   0.317621   0.184522     0.319487
       0.04        0.174760   0.329101   0.188943     0.329062
       0.05        0.185622   0.339251   0.193773     0.330316
      0.075        0.193894   0.332014   0.207885     0.327110
        0.1        0.191344   0.310587   0.212569     0.322807
       0.15        0.196745   0.293783   0.201864     0.315493
        0.2        0.189696   0.274526   0.196893     0.304190
       0.26        0.177025   0.243233   0.177031     0.298652
        0.3        0.176062   0.239891   0.176732     0.297027
       0.36        0.177392   0.219213   0.164453     0.299269
        0.4        0.170361   0.211530   0.165739     0.303160
       0.46        0.171621   0.206189   0.166153     0.305402
        0.5        0.171776   0.205112   0.166378     0.305678
        0.6        0.171188   0.202812   0.158203     0.304631
        0.7        0.173219   0.204808   0.161272     0.308245
        0.8        0.172734   0.200690   0.161046     0.307382
        0.9        0.170475   0.196917   0.149874     0.303362
        1.0        0.177982   0.185807   0.157426     0.300265
        1.3        0.185666   0.185666   0.185666     0.297728
        1.5        0.185940   0.185940   0.185940     0.298167
        1.8        0.186799   0.186799   0.186799     0.299545
        2.0        0.187335   0.187335   0.187335     0.300404
        2.6        0.204828   0.204828   0.204828     0.298586
        3.0        0.216272   0.216272   0.216272     0.288363
    """)



class AmeriEtAl2017RepiStressDrop(AmeriEtAl2017Repi):
    """
    Implements the Ameri et al (2017) GMPE for the case where epicentral
    distance is used, and the stress parameter is specified in the Ground-motion
    logic-tree.
    Example specification of the normalizaed stress parameter:
    <uncertaintyModel>
        [AmeriEtAl2017RepiStressDrop]
        norm_stress_drop = 0.3
    </uncertaintyModel>
    The stress parameter is normalized, according to STRESS_DROP/REF_STRESS_DROP,
    where REF_STRESS_DROP varies regionally. The authors used the following values
    for reference regional stress estimates: 1 bar for the Swtzerland (Swiss Alps+
    Foreland), 10 bars for the French Alps + Rhine Graben, and 100 bars for the 
    Pyrenees events. In this cas, the standard deviation implements a homoscedastic 
    formulation.
    
    Reference:
    Ameri, G., Drouet, S., Traversa, P., Bindi, D., Cotton, F., (2017),
    Toward an empirical ground motion prediction equation for France: 
    accounting for regional differences in the source stress parameter, 
    Bull. Earthquake Eng., 15: 4681-4717.
    """
    REQUIRES_RUPTURE_PARAMETERS = set(('rake', 'mag'))

    def __init__(self, norm_stress_drop, adjustment_factor=1.0):
        super().__init__(adjustment_factor=adjustment_factor)
        self.norm_stress_drop = norm_stress_drop

    def get_mean_and_stddevs(self, sites, rup, dists, imt, stddev_types):
        """
        See :meth:`superclass method
        <.base.GroundShakingIntensityModel.get_mean_and_stddevs>`
        for spec of input and result values.
        """
        # extracting dictionary of coefficients specific to required
        # intensity measure type.

        C = self.COEFFS[imt]
        C_SIGMA = self.COEFFS_SIGMA[imt]
        C_STRESS = self.COEFFS_STRESS[imt]
        imean = self._get_mean(C, C_STRESS, rup, dists, sites)
        # Convert mean to ln(SA) with SA in units of g:
        mean = np.log((10.0 ** (imean - 2.0)) / g)

        istddevs = self._get_stddevs(C_SIGMA, stddev_types, len(sites.vs30), None)
        stddevs = np.log(10.0 ** np.array(istddevs))
        return mean + self.adjustment_factor, stddevs

    def _get_mean(self, C, C_STRESS, rup, dists, sites):
        """
        Returns the mean ground motion
        """
        return (C["a"] + 
                self._get_magnitude_scaling_term(C, rup.mag) +
                self._get_distance_scaling_term(C, dists.repi, rup.mag) +
                self._get_style_of_faulting_term(C, rup.rake) +
                self._get_site_amplification_term(C, sites.vs30) +
                self._get_stress_term(C_STRESS, rup.mag, self.norm_stress_drop))
 

    

