"""
Copyright (C) 2018 contributors listed in AUTHORS.

tvdisaggregator.py
~~~~~

Contains the class TVDisaggregator which is responsible for performing
the full disaggregation of the storage operation.
"""

import sys
import pandas as pd
import numpy as np
import wrapt

from storedisagg import ComponentCalculator

from tqdm import tqdm

from storedisagg import _get_logger

logger = _get_logger(__name__)

tqdm.pandas()


def _check_columns(required_column_set):
    @wrapt.decorator
    def wrapper(f, _, args, kwargs):
        df = kwargs['df'] if 'df' in kwargs else args[0]
        column_set = set(df.columns)
        assert required_column_set.issubset(column_set), ('Method {} requires '
               'input dataframe with columns {}.\n{} were provided.'
               ).format(f.__name__, required_column_set, column_set)

        return f(*args, **kwargs)
    return wrapper


class StDisaggregator():

    @_check_columns({'t', 'chg', 'dch'})
    def __init__(self, df, eff, kind, print_progress=True):

        self._check_is_empty(df)
        self._assert_valid_efficiency(df, eff)

        self.eff = eff
        self.df = df
        self.kind = kind
        self.print_progress = print_progress


    def _assert_valid_efficiency(self, df, eff):

        if self._is_empty:
            logger.warning('Skipping _assert_valid_efficiency. All operation zero.')
        else:
            eff_op = df.dch.sum() / df.chg.sum()
            assert abs(eff_op - eff) / eff < 1e-3, (
                f'Defined efficiency {eff:.4f} does not match '
                f'internal efficiency {eff_op:.4f}')


    def _check_is_empty(self, df):

        chg_tot = df.chg.sum()
        dch_tot = df.dch.sum()

        self._is_empty = not chg_tot and not dch_tot


    def run(self):

        # result dataframes
        self.df_full = None
        self.df_step_evts = None

        self._calc_internal_power()
        self._calc_soc()

        self._shift_profiles()
        self._set_small_to_zero()


        erg = self.df.erg.values
        erg = np.diff(np.concatenate([np.array([erg[-1]]), erg]))
        self.df['ichg_fix'] = self.df['idch_fix'] = erg
        self.df['ichg'] = self.df.ichg_fix.where(self.df.ichg_fix > 0, 0)
        self.df['idch'] = - self.df.idch_fix.where(self.df.idch_fix < 0, 0)

        self._init_result_dfs()

        if not np.all(self.df_step_evts[['res_ichg', 'res_idch']]
                          .applymap(abs)
                          .values.flatten() == 0):

            # calculate aggregate iterations
            self._iterate_event_aggregation()

        self.df_full['ichg_all'] = self.df_full.ichg
        self.df_full['idch_all'] = self.df_full.idch

        # sumcheck: all of these should be equal
        self.df_full[['ichg_all', 'idch_all', 'ichg', 'idch']].sum()
        self.df_step_evts = self.df_step_evts.reset_index(drop=True)
        self._log_totals_aggregation()

        # get hourly components by looping over event rows
        self._loop_get_hourly_components()

        self._generate_stacked_tables()

        # calculate final results consisting in time differences and
        # component values
        self._calc_final_results()

        self._log_totals()







    def _calc_internal_power(self):

        self.df = self.df.rename(columns={'chg': 'echg',
                                          'dch': 'edch'})

        self.df['ichg'] = self.df['echg'] * np.sqrt(self.eff)
        self.df['idch'] = self.df['edch'] / np.sqrt(self.eff)

        # check equality
#        sum_chg = round(self.df.ichg.sum())
#        sum_dch = round(self.df.idch.sum())
#        assert sum_chg == sum_dch, \
#            'Charging doesn\'t match discharging: %f != %f'%(sum_chg, sum_dch)

    def _calc_soc(self):
        '''
        Calculate state-of-charge column erg (units of energy)
        '''

        # calculate SOC
        self.df['erg'] = (self.df.ichg - self.df.idch).cumsum()

        # remove any offset such that the minimum of erg is 0
        self.df['erg'] -= self.df.erg.min()


    def _shift_profiles(self):
        '''
        We want a point of zero state of charge to be at the very beginning.
        '''

        self.zero_t = self.df.loc[self.df.erg == 0, 't'].iloc[-1]
        # shift zero erg to time slot zero
        df_2 = self.df.loc[self.df.t > self.zero_t]
        df_1 = self.df.loc[self.df.t <= self.zero_t]
        self.df = pd.concat([df_2, df_1], sort=True)

        # reset sy column
        self.df = self.df.rename(columns={'t': 't_orig'})
        self.df = (self.df.reset_index(drop=True)
                          .reset_index()
                          .rename(columns={'index': 't'}))


    def _set_small_to_zero(self):

        self.df.loc[self.df.idch.abs() < 1e-9, 'idch'] = 0
        self.df.loc[self.df.ichg.abs() < 1e-9, 'ichg'] = 0


    def _init_result_dfs(self):

        # hourly dataframe df_full to be filled with hourly components
        self.df_full = self.df.copy()
        self.df_full = self.df_full.assign(**{'t_%s'%minmax: self.df_full.t
                                              for minmax in ['min', 'max']})

        # step dataframe with 1 row per charging/discharging pair
        # this is iteration zero of the disaggregation
        logger.debug('Aggregate components iteration 0')
        self.df_step_evts = self.aggregate_events(self.df_full, 0)
        self.df_step_evts['iteration'] = 0


    def _generate_stacked_tables(self):


        self.df_full_stacked = self.df_full.rename(columns={'ichg': 'ichg_res',
                                                            'idch': 'idch_res'})
        # stack df_full table
        ind_list = [c for c in self.df_full_stacked.columns
                    if not any(['_' + str(ii) in c for ii in range(100)])]
        self.df_full_stacked = self.df_full_stacked.set_index(ind_list)
        cols_new = [(int(c.split('_')[1]), c.split('_')[0])
                    for c in self.df_full_stacked.columns]

        self.df_full_stacked.columns = pd.MultiIndex.from_tuples(cols_new)
        self.df_full_stacked = self.df_full_stacked.stack(level=0)
        self.df_full_stacked = self.df_full_stacked.reset_index()

        self.df_full_stacked = self.df_full_stacked.rename(columns={[c for c in
                                                     self.df_full_stacked.columns
                                                     if 'level_' in c][0]:
                                                    'iteration'})
        self.df_full_stacked['kind'] = self.kind
        self.df_step_evts['kind'] = self.kind


    def _calc_final_results(self):

        def get_wgt_center(df, dr):
            '''
            Calculate power weighted center slot.

            Parameters
            ----------
            df - pd.DataFrame
                Power time dataframe with columns ['slot', dr]
            dr - str
                One of {'ichg', 'idch'}
            '''

            return (df[dr] * df.t).sum() / df[dr].sum()


        def get_comp_val(df, dr):
            '''
            Calculate value of components.
            '''

            return (df.mc * df[dr]).sum()


        dfg = self.df_full_stacked.groupby('nevent')

        self.df_step_evts['wgt_center_erg_ichg'] = dfg.apply(get_wgt_center, 'ichg')
        self.df_step_evts['wgt_center_erg_idch'] = dfg.apply(get_wgt_center, 'idch')

        # if the weighted slots are outside [slot_min, slot_max], something
        # is terribly wrong; using tolerance of +- 1e-9 to avoid false positives
        # in case of float accuracy issues for single-time slot components
        mask_outside = \
        ((self.df_step_evts.wgt_center_erg_ichg < self.df_step_evts.t_min - 1 - 1e-9) |
         (self.df_step_evts.wgt_center_erg_ichg > self.df_step_evts.t_max + 1 + 1e-9))
        assert mask_outside.sum() == 0, 'Weighted center outside slot_min/max'

        self.df_step_evts['time_diff_icd'] = (
                self.df_step_evts.wgt_center_erg_idch
                - self.df_step_evts.wgt_center_erg_ichg)

        self.df_step_evts['eff'] = self.eff


    def _log_totals_aggregation(self):

        # comp_dch and comp_chg must add up to the original chg and dch
        logger.info(('Difference idch (events - total):',
              (self.df_step_evts['comp_idch'].sum()
               - self.df_full['idch'].sum())))
        logger.info(('Difference ichg (events - total):',
              (self.df_step_evts['comp_ichg'].sum()
               - self.df_full['ichg'].sum())))
        sys.stdout.flush()


    def _log_totals(self):

        chg_0 = self.df.echg.sum()
        dch_0 = self.df.edch.sum()

        chg_cps = (self.df_step_evts.comp_ichg.sum() / np.sqrt(self.eff)).sum()
        dch_cps = (self.df_step_evts.comp_idch.sum() * np.sqrt(self.eff)).sum()

        logger.info(('Original charging sum   ', chg_0))
        logger.info(('Original discharging sum', dch_0))
        logger.info(('Component discharging sum', chg_cps))
        logger.info(('Component discharging sum', dch_cps))

        sys.stdout.flush()


    def _loop_get_hourly_components(self):

        def get_full_range(x):

            smin = x['t_min']
            smax = x['t_max']
            df_slct = self.df_full.loc[smin:smax]

            return df_slct[['ichg', 'idch']]

        def select_range(row):

            df = self.df_full[['ichg', 'idch']].loc[row.t_min:row.t_max]
            df['iteration'] = row.iteration
            df['nevent'] = row.nevent

            return df

        # get a map (t, iteration) --> nevent
        def expand_t_ranges(x):

            return pd.DataFrame(np.arange(x.t_min, x.t_max + 1))[0]

        # copy nevent column and set column as index
        self.df_step_evts['nevent_index'] = self.df_step_evts.nevent
        self.df_step_evts = self.df_step_evts.set_index('nevent_index')

        # get relevant data and init ComponentCalculator
        def call_compcalc(x, dr, col_nevent):
            nevent = x.name

            val_tgt = self.df_step_evts.loc[nevent, 'comp_' + dr]

            # select residual profile
            y = x[dr]
            y.loc[y < 0] = 0
            y.loc[np.abs(y) < 1e-10] = 0

            # get new component
            self.compcal = ComponentCalculator(y, val_tgt, self.kind, dr)

            return pd.DataFrame({'ycomp': self.compcal.ycomp})


        self.df_full = self.df_full[[c for c in self.df_full.columns
                                     if not 'nevent_' in c]]

        list_iter = self.df_step_evts.iteration.unique()
        for iiter in list_iter:

            col_nevent = 'nevent_%d' % iiter
            df_nevents = (self.df_step_evts.query('iteration == @iiter')
                                           .apply(expand_t_ranges, axis=1)
                                           .stack().reset_index(-1, drop=True)
                                           .reset_index()
                                           .rename(columns={0: 't'})
                                           .set_index(['t'])
                                           .nevent_index.rename(col_nevent))

            self.df_full = self.df_full.join(df_nevents,
                                             on=df_nevents.index.names)

            dr = 'idch'
            for dr in ['idch', 'ichg']:

                col_chgdch = dr + '_' + str(int(iiter))

                df_comp_gp = self.df_full.groupby(col_nevent)

                _, x = list(df_comp_gp)[0]

                call_compcalc_dr = lambda x: call_compcalc(x, dr, col_nevent)

                if self.print_progress:
                    df_comp = df_comp_gp.progress_apply(call_compcalc_dr)
                else:
                    df_comp = df_comp_gp.apply(call_compcalc_dr)

                df_comp = df_comp.reset_index(-1, drop=True)

                if len(df_comp_gp) == 1:
                    df_comp = df_comp.T

                self.df_full[col_chgdch] = df_comp.values.flatten()
                self.df_full[col_chgdch] = self.df_full[col_chgdch].fillna(0)

                self.df_full[dr] -= self.df_full[col_chgdch]


        # Target columns df_full:
        ['t', 'echg', 'edch', 'erg', 'ichg', 'idch', 'mc', 'sy_orig',
       'ichg_fix', 'idch_fix', 't_min', 't_max', 'ichg_all', 'idch_all',
       'nevent_0', 'idch_0', 'ichg_0', 'nevent_1', 'idch_1', 'ichg_1',
       'nevent_2', 'idch_2', 'ichg_2', 'nevent_3', 'idch_3', 'ichg_3',
       'nevent_4', 'idch_4', 'ichg_4', 'nevent_5', 'idch_5', 'ichg_5',
       'nevent_6', 'idch_6', 'ichg_6']

        # Target columns df_step_evts:
        ['comp_ichg', 'comp_idch', 'ichg', 'idch', 'iteration', 'min', 'nevent',
       'res_ichg', 'res_idch', 't_max', 't_min', 'wgt_center_erg_idch',
       'val_comp_idch', 'idch_final', 'wgt_center_erg_ichg', 'val_comp_ichg',
       'ichg_final']


    def _iterate_event_aggregation(self):
        '''
        Iterate block aggregation.

        Note: Iteration 0 corresponds to profile aggregation and is called
        separately.
        '''


        # copy first aggregated table as input to first iteration
        df_step_evts_add = self.df_step_evts.copy()
        iteration = 1
        while len(df_step_evts_add) > 1:
            logger.info('Iteration %d'%iteration)

            df_step_evts_input = df_step_evts_add[['nevent', 'res_ichg',
                                                   'res_idch', 't_min',
                                                   't_max']]

            df_step_evts_input = df_step_evts_input.rename(
                                    columns={'nevent': 't',
                                             'res_ichg': 'ichg',
                                             'res_idch': 'idch'})
            nevent_offset = df_step_evts_input.t.max()
            df_step_evts_add = self.aggregate_events(df_step_evts_input,
                                                     offset=nevent_offset)
            df_step_evts_add['iteration'] = int(iteration)
            iteration += 1

            if df_step_evts_add[['comp_ichg', 'comp_idch']].sum().sum() > 0:
                list_df = [self.df_step_evts, df_step_evts_add]
                self.df_step_evts = pd.concat(list_df, axis=0, sort=True)


    @_check_columns({'t', 'ichg', 'idch'})
    def _add_dummy_rows(self, df):
        '''
        Add first and last zero rows.
        '''

        get_row_df = lambda t: pd.DataFrame(np.array([[t, 0, 0]]),
                                            columns=['t', 'ichg', 'idch'])

        dummy_0 = get_row_df(df.t.min() - 1)
        dummy_end = get_row_df(df.t.max() + 1)

        list_dummy_t = dummy_0.t.tolist() + dummy_end.t.tolist()

        return pd.concat([dummy_0, df, dummy_end], sort=True), list_dummy_t


    @_check_columns({'t', 't_min', 't_max', 'ichg', 'idch'})
    def aggregate_events(self, df, offset=0):
        '''
        Aggregate components either from original profiles
        or subsequent residuals.

        Input dataframe columns: ['slot', 'ichg', 'idch']
        '''

        df, list_dummy_rows = self._add_dummy_rows(df)

        # get onsets of charging/discharging events
        cut_0 = lambda x: max(x, 0)
        df.loc[:, 'ichg_bin'] = (df['ichg'] > 0).apply(int).diff().apply(cut_0)
        df.loc[:, 'idch_bin'] = (df['idch'] > 0).apply(int).diff().apply(cut_0)
                                                  # fillna due to diff
        df = df.loc[-df.t.isin(list_dummy_rows)].fillna(0)

        # filter by onset charging/discharging
        col_slct = ['t', 'ichg_bin', 'idch_bin']
        df_chgs = df.loc[(df.ichg_bin + df.idch_bin) > 0, col_slct]
        df_chgs = df_chgs.loc[(df_chgs.ichg_bin.shift(1) != df_chgs.ichg_bin) &
                              (df_chgs.idch_bin.shift(1) != df_chgs.idch_bin)]

        df = (df.drop(['ichg_bin', 'idch_bin'], axis=1)
                .join(df_chgs.set_index('t'), on='t').fillna(0))

        df['nevent'] = df.ichg_bin.cumsum()
        df.loc[df['nevent'] == 0, ['nevent']] = 1
        df['nevent'] += offset

        # get total energy as well as min/max slot -> rows of df_step_evts
        df_evts = df.pivot_table(index=['nevent'],
                                 values=['ichg', 'idch', 't_min', 't_max'],
                                 aggfunc={'idch': 'sum', 'ichg': 'sum',
                                          't_min': 'min', 't_max': 'max'}
                                 ).reset_index()

        # calculate component energy from minima
        df_evts['min'] = df_evts[['ichg', 'idch']].min(axis=1)
        df_evts['comp_ichg'] = df_evts['comp_idch'] = df_evts['min']
        df_evts['res_ichg'] = df_evts['ichg'] - df_evts['comp_ichg']
        df_evts['res_idch'] = df_evts['idch'] - df_evts['comp_idch']

        # set very small residual energies to zero
        df_evts.loc[df_evts.res_ichg < 1e-3, 'res_ichg'] = 0
        df_evts.loc[df_evts.res_idch < 1e-3, 'res_idch'] = 0

        return df_evts


    def final_tables_to_sql(self):
        ''' Writes the two result tables to the database. '''


        for itb in ['step_evts_all', 'full_all']:

            aql.joinon(self.db, ['pp', 'nd_id'], ['pp_id'],
                       [self.sc_out, itb], [self.sc, 'def_plant'])

            aql.joinon(self.db, ['nd'], ['nd_id'],
                       [self.sc_out, itb], [self.sc, 'def_node'])


if __name__ == '__main__':


    import time

    irun = 0
    ipp = 256

    df_raw = pd.read_hdf(sc_out, 'var_sy_pwr',
                         where='run_id == {} and pp_id == {}'.format(irun, ipp))

    df = df_raw.pivot_table(columns='bool_out', values='value', index='sy') * 1e6
    df = df.rename(columns={True: 'echg', False: 'edch'}).reset_index()
    df['mc'] = 1

    t = time.time()

    tvd = StDisaggregator(df, 0.9, 'share')

    self = tvd

    self.run()

    print(time.time() - t)
