"""
Copyright (C) 2018 contributors listed in AUTHORS.

compcalc.py
~~~~~

Contains the class ComponentCalculator which serves to define the
component charging and discharging profiles.
"""


from scipy.optimize import minimize
import numpy as np
import pandas as pd

class ComponentCalculator:
    '''
    Defines methods to extract components with specified total area/energy
    val_tgt. Final compon
    '''

    def __init__(self, y, val_tgt, kind, dr):

        # standardize chg/dch column name
        dr = [c for c in ['chg', 'dch'] if c in dr][0]

        # define dict kind -> sub_kind
        dict_sub_kind = {'leftright': {'chg': 'left', 'dch': 'right'},
                         'rightleft': {'chg': 'right', 'dch': 'left'},
                         'top': {'chg': 'top', 'dch': 'top'},
                         'bottom': {'chg': 'bottom', 'dch': 'bottom'},
                         'share': {'chg': 'share', 'dch': 'share'}}

        dict_method = {'leftright': self.get_component_leftright,
                       'rightleft': self.get_component_leftright,
                       'top': self.get_component_topbottom,
                       'bottom': self.get_component_topbottom,
                       'share': self.get_component_share}

        # select method
        method_slct = dict_method[kind]

        self.ycomp = method_slct(y, val_tgt, dict_sub_kind[kind][dr])

    def get_component_topbottom(self, y, val_tgt, sub_kind):
        ''' Component is cut from the top or from the bottom. '''

        def func_topbottom(y, lim, kind):
            if kind == 'top':
                if lim > y.max():
                    # Bad things happen if lim > y.max()
                    # and the objective function becomes zero!
                    yret = y * 0 + lim
                else:
                    yret = np.maximum(y - lim, 0)
            elif kind == 'bottom':
                if lim >= y.max():
                    yret = y * 0 + lim
                else:
                    yret = np.minimum(y, lim)
            return yret

        def func_min_tb(x, y, val_tgt, kind):
            ret = abs(func_topbottom(y, lim=x, kind=kind).sum() - val_tgt)
            return ret

        y = np.array(y)

        result = minimize(func_min_tb, 0, method='Nelder-Mead',
                          args=(y, val_tgt, sub_kind))

        # get level
        lvl = result.x[0]

        # calculate component profile from level
        yret = func_topbottom(y, lvl, sub_kind)

        return yret

    def get_component_share(self, y, val_tgt, sub_kind):
        ''' New component is simply the scaled y.'''

        y = np.array(y)
        yret = y * val_tgt / y.sum()

        return yret

    def get_component_leftright(self, y, val_tgt, sub_kind):
        ''' Component is cut from the left or from the right. '''

        y.loc[y.abs() < 1e-9] = 0

        y = np.array(y)

        if sub_kind == 'right':
            ylr = np.array([y[yy] for yy in np.arange(len(y) - 1, -1, -1)])
        elif sub_kind == 'left':
            ylr = np.array([y[yy] for yy in np.arange(len(y))])

        # construct df with original profile and cumsum
        dfcs_0 = pd.DataFrame(np.array([ylr, ylr.cumsum()]).T,
                              columns=['val', 'cumsum'])

        dfcs = dfcs_0.copy()
        dfcs['val_comp'] = 0

        # get values where cumsum smaller target
        mask = dfcs_0['cumsum'] < val_tgt
        dfcs.loc[mask, 'val_comp'] = dfcs_0['val']

        flag_complete = False
        if mask.sum() == 0:
            next_ind = 0
        elif mask.sum() == len(mask):
            flag_complete = True
        else:
            next_ind = dfcs.loc[mask].index.get_values().max() + 1

        # get total of this selection
        valsum_0 = dfcs['val_comp'].sum()

        # add residual to next row
        if not flag_complete:
            dfcs.iloc[next_ind, -1] = val_tgt - valsum_0

        yret = np.array(dfcs.val_comp)

        # flip yret if required
        if sub_kind == 'right':
            slct_index = np.arange(len(yret) - 1, -1, -1)
        elif sub_kind == 'left':
            slct_index = np.arange(len(yret))
        yret = np.array([yret[yy] for yy in slct_index])

        return yret


