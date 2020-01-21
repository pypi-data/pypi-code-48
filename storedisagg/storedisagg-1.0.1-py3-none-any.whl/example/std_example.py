#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 26 17:31:59 2018

@author: user
"""
import sys
import pandas as pd
import numpy as np
from importlib import reload


import storedisagg as std

reload(std)

sys.exit()


df = std.get_example_data_100()

fig, ax = plt.subplots(1, 2)



dfplot = df.set_index('sy').assign(Discharging=-df['edch'], Charging=df['echg'])
print(dfplot)

dfplot['Stored energy'] = dfplot[['Charging', 'Discharging']].sum(axis=1).cumsum()

dfplot[['Charging', 'Discharging']].plot.area(ax=ax[0])
dfplot[['Stored energy']].plot.area(ax=ax[1])
for iax, ylab in enumerate(['Power', 'Energy']): ax[iax].set_ylabel(ylab)





# %%


df = tvd.df_full.loc[tvd.df_full.kind == 'share'].copy()
dfstp = tvd.df_step_evts.loc[tvd.df_step_evts.kind == 'share'].copy()
df['dch'] = df['idch']
df['chg'] = df['ichg']
dfstp['wgt_center_erg_dch'] = dfstp['wgt_center_erg_idch']
dfstp['wgt_center_erg_chg'] = dfstp['wgt_center_erg_ichg']

df['chgdch'] = df.chg - df.dch

dfstp['iteration'] += 1
df['iteration'] += 1

    # get erg by iteration
df['erg_new'] = df.groupby(['iteration'])[['chgdch']].cumsum()

dfeg_iter = df.pivot_table(values=['erg_new'], index=['iteration', 'slot'], aggfunc=sum)
dfeg_iter[dfeg_iter < 0] = 0
dfeg_iter = dfeg_iter.reset_index()
dfeg_iter['type'] = 'zdisagg'

dfeg_all = df.pivot_table(values=['erg'], index=['slot'], aggfunc=np.mean)
dfeg_all[dfeg_all< 0] = 0
dfeg_all = dfeg_all.reset_index()
dfeg_all['iteration'] = 'all'
dfeg_all['type'] = 'total'

dfeg = pd.concat([dfeg_iter.rename(columns={'erg_new': 'erg'}), dfeg_all], axis=0, sort=True)
dfeg['pwrerg'] = 'erg'


dfcd_comp = df.pivot_table(values=['chg', 'dch'], index=['nevent', 'iteration', 'slot'])
dfcd_comp[dfcd_comp < 0] = 0
dfcd_comp['dch'] *= -1
dfcd_comp = dfcd_comp.reset_index()
dfcd_comp['type'] = 'zdisagg'

dfcd_all = df.pivot_table(values=['chg', 'dch'], index=['slot'], aggfunc=sum)
dfcd_all[dfcd_all < 0] = 0
dfcd_all = dfcd_all.reset_index()
dfcd_all['chg'] -= dfcd_all['dch']
dfcd_all['dch'] = np.nan
dfcd_all['nevent'] = 'all'
dfcd_all['iteration'] = 'all'
dfcd_all['type'] = 'total'

dfcd = pd.concat([dfcd_comp, dfcd_all], axis=0, sort=True)
dfcd['pwrerg'] = 'pwr'


dfdiff = dfstp.set_index(['nevent', 'iteration'])[['wgt_center_erg_dch', 'wgt_center_erg_chg']].stack().reset_index()
dfdiff['level_2'] = dfdiff.level_2.apply(lambda x: x.split('_')[-1])
dfdiff = dfdiff.rename(columns={'level_2': 'chgdch', 0: 'slot'})
dfdiff['type'] = 'ctr'
dfdiff['center'] = 0

# %%


from matplotlib import cm
import matplotlib as mpl

reload(pltpg)
reload(maps)

mps = maps.Maps('out_marg_store', 'storage2', color_style='p2')

data_kw = {'data_scale': {'chg': -1}, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['pwrerg'], ind_plty=['_name'],
               name='total', series=['type'], values=['chg', 'dch'])

do_pwrtot = pltpg.PlotPageData.from_df(df=dfcd.loc[dfcd.type == 'total'], **indx_kw, **data_kw)

indx_kw = dict(ind_axx=['slot'], ind_pltx=['pwrerg'], ind_plty=['_name'],
               name='total', series=['type'], values=['erg'])
do_ergtot = pltpg.PlotPageData.from_df(df=dfeg.loc[dfeg.type == 'total'], **indx_kw, **data_kw)

data_kw = {'data_scale': {'chg': -1}, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['pwrerg'], ind_plty=['_name'],
               name='nevent', series=['nevent'], values=['chg', 'dch'], series_order=[2,1])
do_pwrnevent = pltpg.PlotPageData.from_df(df=dfcd.loc[dfcd.type == 'zdisagg'], **indx_kw, **data_kw)
do_pwrnevent.data.columns = [(col[0], 'event_%d' %col[1]) for col in do_pwrnevent.data.columns]


dfei = do_pwrnevent.data_raw_0.copy()
dfei['erg'] = dfei.groupby('nevent').apply(lambda x: x[['chg', 'dch']].sum(axis=1).cumsum()).reset_index(drop=True)
dfei['pwrerg'] = 'erg'
data_kw = {'data_scale': {'chg': -1}, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['pwrerg'], ind_plty=['_name'],
               name='nevent', series=['nevent'], values=['erg'])
do_ergnevent = pltpg.PlotPageData.from_df(df=dfei, **indx_kw, **data_kw)
do_ergnevent.data.columns = [(col[0], 'event_%d' %col[1]) for col in do_ergnevent.data.columns]

data_kw = {'data_scale': {'chg': -1}, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['pwrerg'], ind_plty=['_name'], series_order=[1,0],
               name='iteration', series=['iteration'], values=['chg', 'dch'])
do_pwriter = pltpg.PlotPageData.from_df(df=dfcd.loc[dfcd.type == 'zdisagg'], **indx_kw, **data_kw)
do_pwriter.data.columns = [(col[0], 'iter_%d' %col[1]) for col in do_pwriter.data.columns]

dfei = do_pwriter.data_raw_0.copy()
dfei['erg'] = dfei.groupby('iteration').apply(lambda x: x[['chg', 'dch']].sum(axis=1).cumsum()).reset_index(drop=True)
dfei['pwrerg'] = 'erg'
data_kw = {'data_scale': {'chg': -1}, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['pwrerg'], ind_plty=['_name'],
               name='iteration', series=['iteration'], values=['erg'])
do_ergiter = pltpg.PlotPageData.from_df(df=dfei, **indx_kw, **data_kw)
do_ergiter.data.columns = [(col[0], 'iter_%d' %col[1]) for col in do_ergiter.data.columns]

data_kw = {'data_scale': {'chg': -1}, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['_name'], ind_plty=['type'], name='pwr',
               series=['nevent'], values=['chg', 'dch'])
do_pwr = pltpg.PlotPageData.from_df(df=dfcd, **indx_kw, **data_kw)
do_pwr.data.loc[('pwr', 'total'), ('dch', 'all')] = np.nan


indx_kw = dict(ind_axx=['slot'], ind_pltx=['_name'], ind_plty=['type'], name='erg',
               series=['iteration'], values=['erg'])
do_erg = pltpg.PlotPageData.from_df(df=dfeg, **indx_kw, **data_kw)

indx_kw = dict(ind_axx=['slot'], ind_pltx=['_name'], ind_plty=['type'], name='pwr',
               series=['iteration'], values=['center'])
do_ctr = pltpg.PlotPageData.from_df(df=dfdiff, **indx_kw, **data_kw)


do_pwrtot.data = do_pwrtot.data.fillna(0)
do_ergtot.data = do_ergtot.data.fillna(0)
do_ergiter.data = do_ergiter.data.fillna(0)
do_pwriter.data = do_pwriter.data.fillna(0)
do_ergnevent.data = do_ergnevent.data.fillna(0)
do_pwrnevent.data = do_pwrnevent.data.fillna(0)

do = do_pwrtot + do_ergtot + do_ergiter + do_pwriter + do_ergnevent + do_pwrnevent

#do.data = do.data.fillna(0)


# reverse order all events, all iterations
do.data = do.data[[col for col in do.data.columns if 'total' in col] + [col for itrevt in reversed(range(10)) for col in do.data.columns if 'iter_%s' %itrevt in col or 'event_%s' %itrevt in col]]

colors = {'event_1': mps.c2, 'event_2': mps.c3, 'event_3': mps.c4, 'event_4': mps.c5,
          'event_5': mps.c1, 'event_6': mps.c9, 'all': mps.c5,
          'iter_1': mps.c1, 'iter_2': mps.c9, 'total': mps.c5}


layout_kw = {'left': 0.05, 'right': 0.98, 'wspace': 0.12,
             'hspace': 0.12, 'bottom': 0.05, 'page_dim': (9/2.54, 4),
             'width_ratios': [3.5,2]
             }
label_kw = {'label_format':False, 'label_subset':[-1], 'label_threshold':1e-6,
            'label_ha': 'left'}
plot_kw = dict(kind_def='StackedArea', on_values=True, #draw_now=False,
#               kind_dict={('erg', 'total'): 'plot.line'},
               stacked=True, sharex=True, sharey=False, linewidth=0,
               colormap=colors,#color_comp,
               barwidth=1, xlabel='',
               opacitymap=1, edgecolor=mps.c2,
               reset_xticklabels=False, caption=False,
               marker=None, legend='none',
               )



#with plt.style.context(('ggplot')):
plt_0 = pltpg.PlotTiled(do, **plot_kw, **layout_kw, **label_kw)
#self = plt_0.plotdict[(('pwr',), ('total',), 'plot.bar')]
#
#self.data.plot()
#
#import grimsel_h.plotting.plotting as lpplt
#lpplt.StackedArea(plt_0.current_plot.data, ax=self.ax)

# %


ax = plt_0.plotdict[(('pwr',), ('nevent',), 'StackedArea')].ax
ax.set_ylim(bottom=-1.4)

arrows = dfstp.set_index('nevent')[['iteration', 'wgt_center_erg_ichg', 'wgt_center_erg_idch', 'time_diff_icd']]
arrows.columns = ['iter', 'from', 'to', 'diff']

arrows = arrows.join(dfcd.loc[dfcd.type == 'zdisagg']
                         .groupby('nevent')['dch'].min().rename('min'))


# special coordinates for the iteration=1 split
coords_special = (dfcd.loc[(dfcd.type == 'zdisagg') & dfcd.slot.isin([32, 40])]
                      .groupby(['slot']).sum()
                      .reset_index()[['dch', 'slot']]
                      .rename(columns={'dch': 'y', 'slot': 'x'})).set_index('x')

def dashed_line(xy_start, xy_end):
    ax.annotate('',
        xy=xy_start, xytext=xy_end,
        verticalalignment='center',
        horizontalalignment='right',
        arrowprops=dict(arrowstyle='-', color='k', linestyle='dotted',
                        linewidth=mpl.rcParams['lines.linewidth'])
        )

def solid_line(xy_start, xy_end):
    ax.annotate('',
        xy=xy_start, xytext=xy_end,
        verticalalignment='center',
        horizontalalignment='right',
        arrowprops=dict(arrowstyle='-', color='k', linestyle='-',
                        linewidth=mpl.rcParams['lines.linewidth'])
        )
def arrow_line(xy_start, xy_end):
    ax.annotate('',
                xy=xy_start, xytext=xy_end,
                verticalalignment='center',
                horizontalalignment='right',
                arrowprops=dict(arrowstyle='<-', color='k',
                                linewidth=mpl.rcParams['lines.linewidth'])
                )



offset = -1.1
for nevent, row in arrows.iterrows():
    rowdict = row.to_dict()

    xy_start = np.array((rowdict['from'], 0.2 * (1 - rowdict['iter']) + offset))
    xy_end = np.array((rowdict['to'], 0.2 * (1 - rowdict['iter']) + offset))



    if nevent in [1,2,3,4]:
        yoffs = 0.05
        rot = 90
        unit = ''
    else:
        yoffs = 0
        rot = 0
        unit = ' hours'


    ax.text(*(0.5 * (xy_start + xy_end) + np.array([0, yoffs])),
             '{:.1f}'.format(rowdict['diff']) + unit,
             horizontalalignment='center',
             verticalalignment='bottom',
             rotation=rot)

    arrow_line(xy_start, xy_end)



    # vertical lines
    for xy, y_dashed in [(xy_start, 0), (xy_end, rowdict['min'])]:

        if nevent == 6 and y_dashed < 0:
            y_dashed *= 3
            for x, y in coords_special.iterrows():

                dashed_line((xy[0], y_dashed), (x, y))

        dashed_line((xy[0], y_dashed), (xy[0], xy[1] - 0.05))

dict_ylabel = {'erg': 'Stored Energy (MWh)',
               'pwr': 'Charging/discharging power (MW)'}

dict_title = {('pwr', 'iteration'): 'Power, disaggregated by iteration',
              ('erg', 'iteration'): 'Energy',
              ('pwr', 'nevent'): 'Power, uninterrupted sub-components',
              ('erg', 'nevent'): 'Energy',
              ('pwr', 'total'): 'Power, original profile',
              ('erg', 'total'): 'Energy',}



dict_ncol = {'iteration': 1, 'nevent': 2, 'total': 1}

for nx, ix, ny, iy, plot, ax, kind in plt_0.get_plot_ax_list():



    indaxx = plot.data.index.get_level_values('slot')
    ax.plot([indaxx.min(), indaxx.max()], [0, 0], color=mps.c2, linewidth=1)


    ax.set_ylabel(dict_ylabel[ix[0]])

    nn = nx + 2 * ny
    add_subplotletter(ax, nn, loc=(0.02,0.98))

    if ny == 2:
        ax.set_xlabel('Hour')

    ax.set_title(dict_title[(*ix, *iy)])

    ax.set_yticklabels([])

    hh, ll = plot.ax.get_legend_handles_labels()

    if 'erg' in ix:

        lgd_name = '#'

        ll = [l.split('\'')[-2].replace('event_', '#').replace('iter_', '#').replace('total', 'Original profile') for l in ll]

        ax.legend(reversed(hh), reversed(ll), ncol=dict_ncol[iy[0]], loc=1)


# %% Comparison kinds


df = tvd.df_full.loc[tvd.df_full.slot < 48].copy()


#df.loc[df.iteration.isin([6]) & df.kind.isin(['bottom'])].set_index('slot')['chgdch'].plot()

df['chg'] = df['ichg']
df['dch'] = df['idch']

df['chgdch'] = df.chg - df.dch

df['iteration'] += 1
dfstp = tvd.df_step_evts.copy()

df['erg_new'] = df.groupby(['iteration'])[['chgdch']].cumsum()

dfeg_iter = df.pivot_table(values=['erg_new'], index=['iteration', 'slot', 'kind'], aggfunc=sum)
dfeg_iter[dfeg_iter < 0] = 0
dfeg_iter = dfeg_iter.reset_index()
dfeg_iter['type'] = 'zdisagg'

dfeg_iter.plot()

from matplotlib import cm
import matplotlib as mpl


reload(pltpg)
reload(maps)

mps = maps.Maps('out_marg_store', 'storage2', color_style='p2')

data_kw = {'data_scale': 1, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['_name'], ind_plty=['kind'], name='pwr',
               series=['nevent'], values=['chgdch'])
docd = pltpg.PlotPageData.from_df(df=df.loc[df.kind != 'top'], **indx_kw, **data_kw)
docd.data.columns = [(c[0], 'event_%d'%c[1]) for c in  docd.data.columns]

indx_kw['series_order'] = [6,1,2,3]
indx_kw['values'] = ['chgdch_top']
docd_top = pltpg.PlotPageData.from_df(df=df.loc[df.kind == 'top'].rename(columns={'chgdch': 'chgdch_top'}), **indx_kw, **data_kw)
docd_top.data.columns = [(c[0], 'event_%d'%c[1]) for c in  docd_top.data.columns]



srs_order= [2,1]
data_kw = {'data_scale': 1, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['slot'], ind_pltx=['_name'], ind_plty=['kind'], name='erg',
               series=['iteration'], values=['erg_new'], series_order=srs_order)
doeg = pltpg.PlotPageData.from_df(df=dfeg_iter, **indx_kw, **data_kw)
doeg.data.columns = [(c[0], 'iter_%d'%c[1]) for c in  doeg.data.columns]

do = doeg + docd + docd_top

colors = {'event_1': mps.c2, 'event_2': mps.c3, 'event_3': mps.c4, 'event_4': mps.c5,
          'event_5': mps.c1, 'event_6': mps.c9, 'all': mps.c5,
          'iter_1': mps.c1, 'iter_2': mps.c9, 'total': mps.c5}



do.data = do.data.fillna(0)


layout_kw = {'left': 0.05, 'right': 0.98, 'wspace': 0.15,
             'hspace': 0.1, 'bottom': 0.05, 'page_dim': (9/2.54, 4),
             'width_ratios': [2,3]}
label_kw = {'label_format':False, 'label_subset':[-1], 'label_threshold':1e-6,
            'label_ha': 'left'}
plot_kw = dict(kind_def='StackedArea',
#               plotkwargsdict=plotkwargsdict,
               stacked=True, sharex=True, sharey=False, linewidth=0,
               colormap=colors, on_values=False, edgecolor=None, edgewidth=0,
               barwidth=1, xlabel='',
               opacitymap=1, #edgecolor=mps.c2,
               reset_xticklabels=False, caption=False,
               legend='False', marker=None)
plt_0 = pltpg.PlotTiled(do, **layout_kw, **label_kw, **plot_kw)



# %
for nx, ix, ny, iy, plot, ax, kind in plt_0.get_plot_ax_list():

    indaxx = plot.data.index.get_level_values('slot')
    ax.plot([indaxx.min(), indaxx.max()], [0, 0], color=mps.c2, linewidth=1)


    ax.set_yticklabels([])

    ax.set_ylim(bottom=-0.9)

    if ny == 2:
        ax.set_ylabel(dict_ylabel[ix[0]])
    else:
        ax.set_ylabel('')

    if ny == len(do.list_ind_plty) - 1:
        ax.set_xlabel('Hour')


    if ny == 0:
        ax.set_title({'pwr': 'Charging/discharging power components',
                      'erg': 'Stored energy by iteration'}[ix[0]])
    else:
        ax.set_title('')


    # kind label
    if 'erg' in ix:
        ax.text(0.02, .85, iy[0],
                horizontalalignment='left',
                transform=ax.transAxes)

    if ny == 0:

        hh, ll = plot.ax.get_legend_handles_labels()


        lgd_name = '#'

        print(ix)
        filt_pwrerg = 'chgdch' if 'pwr' in ix else 'erg'

        # remove duplicates chg/dch
        hh, ll = list(zip(*[(hh, ll) for hh, ll in zip(hh, ll)
                   if filt_pwrerg in ll]))


        make_float = lambda x: x.isdigit() or x == '.'
        ll = [lgd_name + '%d' %int(float(''.join(list(filter(make_float, l))))) for l in ll]

        ll, hh = list(zip(*[(l, h) for l, h in {l: h for l, h in zip(ll, hh)}.items()]))


        ax.legend(hh, ll, ncol=2, loc=1)


    arrows = dfstp.loc[dfstp.iteration.isin([1])
                     & dfstp['kind'].isin([iy[0]])
                      ].set_index('nevent')[['iteration', 'wgt_center_erg_ichg', 'wgt_center_erg_idch', 'time_diff_icd']]
    arrows.columns = ['iter', 'from', 'to', 'diff']

    arrows = arrows.join(dfcd.loc[dfcd.type == 'zdisagg']
                             .groupby('nevent')['dch'].min().rename('min'))


    dict_split = {'special_slots': {'top': [32,41],
                                    'share': [31, 41],
                                    'leftright': [28, 41],
                                    'rightleft': [33, 43],
                                    'bottom': [32, 41],},
                  'sum': {'top': False,
                          'share': True,
                          'leftright': True,
                          'rightleft': True,
                          'bottom': True}}


    # special coordinates for the iteration=1 split
    coords_special = dfcd.loc[(dfcd.type == 'zdisagg')
                             & dfcd.slot
                                   .isin(dict_split['special_slots'][iy[0]])]
    if dict_split['sum'][iy[0]]:
        coords_special = (coords_special.groupby(['slot']).sum()
                                        .reset_index()[['dch', 'slot']])
    else:
        coords_special = coords_special.loc[coords_special.nevent == 6,
                                            ['dch', 'slot']]
    coords_special = (coords_special.rename(columns={'dch': 'y', 'slot': 'x'})
                                    .set_index('x'))



    offset = -0.8
    if 'pwr' in ix:
        for nevent, row in arrows.iterrows():
            rowdict = row.to_dict()

            xy_start = np.array((rowdict['from'], 0.15 * (1 - rowdict['iter']) + offset))
            xy_end = np.array((rowdict['to'], 0.15 * (1 - rowdict['iter']) + offset))

            ax.text(*(0.5 * (xy_start + xy_end) + np.array([0, 0])),
                     '{:.1f}'.format(rowdict['diff']) + 'hours',
                     horizontalalignment='center',
                     verticalalignment='bottom')

            arrow_line(xy_start, xy_end)


            # vertical lines
            for xy, y_dashed in [(xy_start, 0), (xy_end, rowdict['min'])]:

                if nevent == 6 and y_dashed < 0:
                    y_dashed *= 3
                    for x, y in coords_special.iterrows():

                        dashed_line((xy[0], y_dashed), (x, y))

                dashed_line((xy[0], y_dashed), (xy[0], xy[1] - 0.05))


# %%
reload(pltpg)

colors = {'event_1': mps.c2, 'event_2': mps.c3, 'event_3': mps.c4, 'event_4': mps.c5,
          'event_5': mps.c1, 'event_6': mps.c9, 'all': mps.c5,
          'iter_1': mps.c1, 'iter_2': mps.c9, 'total': mps.c5,
          'chg': mps.c1, 'dch': mps.c3}

slct_kind = ['share']

df = df_full_all.loc[tvd.df_full.kind.isin(slct_kind)
#                        & tvd.df_full.iteration.isin([0])
                        ].copy()


df['chg'] = df['ichg']
df['dch'] = df['idch']
df['chgdch'] = df.chg - df.dch
df['iteration'] += 1

# adding second iteration to first
df_prof_all = df.pivot_table(values=['chg', 'dch'], index='slot', columns=['iteration', 'nevent'], aggfunc=np.sum).stack(level=0)
df_prof_all = np.add(df_prof_all.xs(1, level='iteration', axis=1),
                     df_prof_all.xs(2, level='iteration', axis=1))
df_prof_all = df_prof_all.stack().reset_index().rename(columns={'level_1': 'chgdch', 0: 'value'})


# First aggregation
df_agg_0 = df_prof_all.pivot_table(index=['chgdch', 'nevent'], values='value', aggfunc=sum).reset_index()

# First component
df_cmp_0 = df_agg_0.pivot_table(index=['nevent'], values='value', aggfunc=min).reset_index()
df_cmp_0['chgdch'] = 'chg'
df_cmp_0 = pd.concat([df_cmp_0, df_cmp_0.assign(chgdch='dch')], axis=0)

# First residual
df_res_0 = df_agg_0.set_index(['nevent', 'chgdch']) - df_cmp_0.set_index(['nevent', 'chgdch'])
df_res_0 = df_res_0.reset_index()
df_res_0.loc[df_res_0.value < 1e-3, 'value'] = 0

# second aggregation
df_agg_1 = df.loc[df.iteration == 2].pivot_table(index=['nevent'],
                                                 values=['chg', 'dch'],
                                                 aggfunc=sum)
df_agg_1 = df_agg_1.stack().reset_index().rename(columns={'level_1': 'chgdch',
                                                   0: 'value'})

# Second component
df_cmp_1 = df_agg_1.pivot_table(index=['nevent'], values='value', aggfunc=min).reset_index()
df_cmp_1['chgdch'] = 'chg'
df_cmp_1 = pd.concat([df_cmp_1, df_cmp_1.assign(chgdch='dch')], axis=0)


# add min/max slot and center
dfstp = df_step_evts_all.loc[tvd.df_step_evts.kind.isin(slct_kind)]
df_minmax_prf= df.loc[df.chgdch != 0].pivot_table(index=['nevent', 'iteration'],
                          values=['slot'], aggfunc=[min, max])
df_minmax_prf.columns = ['_'.join(c) for c in df_minmax_prf.columns]
df_minmax_prf = df_minmax_prf.reset_index()

# First difference
df_minmax_agg = df_res_0.loc[df_res_0.value != 0].pivot_table(values='nevent', aggfunc=[min, max], index='chgdch')
df_minmax_agg.columns = ['_'.join(c) for c in df_minmax_agg.columns]





data_kw = {'data_scale': 1, 'aggfunc': np.sum, 'data_threshold': 1e-10}
indx_kw = dict(ind_axx=['nevent'], ind_pltx=[], ind_plty=['_name'], ind_axy=['chgdch'],
               series=['cd'], )
do_agg_0 = pltpg.PlotPageData.from_df(df=df_agg_0.assign(cd=df_agg_0.chgdch), values=['value'], **indx_kw, **data_kw, name='bars_value_0')
do_cmp_0 = pltpg.PlotPageData.from_df(df=df_cmp_0.assign(cd=df_cmp_0.chgdch), values=['value'], **indx_kw, **data_kw, name='bars_value_comp_0')
do_res_0 = pltpg.PlotPageData.from_df(df=df_res_0.assign(cd=df_res_0.chgdch), values=['value'], **indx_kw, **data_kw, name='bars_value_res_0')
do_agg_1 = pltpg.PlotPageData.from_df(df=df_agg_1.assign(cd=df_agg_1.chgdch), values=['value'], **indx_kw, **data_kw, name='bars_value_1')
do_cmp_1 = pltpg.PlotPageData.from_df(df=df_cmp_1.assign(cd=df_cmp_1.chgdch), values=['value'], **indx_kw, **data_kw, name='bars_value_comp_1')


####### PLOTTING #######

reload(pltpg)

do_agg_0.data = do_agg_0.data.fillna(0)

plot_kw = dict(kind_def='StackedGroupedBar',
               stacked=False, sharex=False, sharey=False, linewidth=0,
               colormap=colors, #space = 0.1,
               barwidth=0.4, title='', ylabel='Energy (MWh)',
               opacitymap=1, edgecolor=mps.c2,
               reset_xticklabels=True, caption=False, xlim=(-0.5, 4.5),
               legend='False', marker=None, draw_now=False)
plt_agg_0 = pltpg.PlotTiled(do_agg_0, **label_kw, **plot_kw)
plt_cmp_0 = pltpg.PlotTiled(do_cmp_0, **label_kw, **plot_kw)
plt_res_0 = pltpg.PlotTiled(do_res_0, **label_kw, **plot_kw)
plt_agg_1 = pltpg.PlotTiled(do_agg_1, **label_kw, **plot_kw)
plt_cmp_1 = pltpg.PlotTiled(do_cmp_1, **label_kw, **plot_kw)
# %
indx_kw = dict(ind_axx=['slot'], ind_pltx=[], ind_plty=['_name'],
               series=['chgdch'], values=['value'], name='prof')
do_profile = pltpg.PlotPageData.from_df(df=df_prof_all, **indx_kw, **data_kw)

plot_kw = dict(kind_def='StackedArea',
#               plotkwargsdict=plotkwargsdict,
               stacked=True, sharex=True, sharey=False, linewidth=0,
               colormap=colors,
               barwidth=1, title='', ylabel='Power (MW)',
               opacitymap=1, edgecolor=mps.c2,
               reset_xticklabels=False, caption=False,
               legend='False', marker=None, draw_now=False)
plt_prf = pltpg.PlotTiled(do_profile, **plot_kw)


layout_kw = {'left': 0.05, 'right': 0.98, 'wspace': 0.15,
             'hspace': 0.2, 'bottom': 0.06, 'page_dim': (9/2.54, 4),
#             'width_ratios': [2,]
             }

plt_1 = pltpg.PlotTiled.concat([plt_agg_0, plt_cmp_0], concat_dir='x', **layout_kw, draw_now=False)
plt_2 = pltpg.PlotTiled.concat([plt_agg_1, plt_cmp_1], concat_dir='x', **layout_kw, draw_now=False)

plt_tot = pltpg.PlotTiled.concat([plt_prf, plt_1, plt_res_0, plt_2], concat_dir='y', **layout_kw, sharey='row')


# %

from matplotlib.patches import ConnectionPatch



plot_bars_value_0 = plt_tot.plotdict[((0,), ('bars_value_0',), 'StackedGroupedBar')]
plot_prof = plt_tot.plotdict[((0,), ('prof',), 'StackedArea')]
plot_bars_res_0 = plt_tot.plotdict[((0,), ('bars_value_res_0',), 'StackedGroupedBar')]
plot_bars_value_1 = plt_tot.plotdict[((0,), ('bars_value_1',), 'StackedGroupedBar')]

plot_prof.ax.xaxis.tick_top()
plot_prof.ax.set_xlabel('Hours')
plot_prof.ax.xaxis.set_label_position('top')

# %

# ylim bars and xlim iter 0
ylim_bars = (-0.2, plot_bars_value_0.ax.get_ylim()[1])
xlim_iter_0 = plot_bars_value_0.ax.get_xlim()

dict_label = {'comp': (0.05, 'left', 'Minimum'),
              'res': (0.95, 'right', 'Residual'),
              'prof': (0.05, 'left', 'Original profile'),
              'default': (0.05, 'left', 'Aggregate')}

for kk, plot in plt_tot.plotdict.items():

    plot.ax.set_yticklabels([])

    if '_1' in kk[1][0]:
        plot.ax.set_xlim(np.array(xlim_iter_0) - 2)

        plot.ax.set_xticklabels([6], rotation=0)
        xticks = plot.ax.xaxis.get_major_ticks()
        xticks[-1].set_visible(False)

    if '_0' in kk[1][0]:
        plot.ax.set_xticklabels(range(1, 6), rotation=0)

    if 'StackedGroupedBar' in kk:
        plot.ax.set_ylim(ylim_bars)


        if '_comp_' in kk[1][0]:
            plot.ax.set_title('Component energy iteration %d'%(int(kk[1][0].split('_')[-1]) + 1))
            plot.ax.set_xlabel('Component')
        else:
            plot.ax.set_title('')
            plot.ax.set_xlabel('')
            if '_1' in kk[1][0]:
                plot.ax.set_xlabel('Component')

    label_keys = [key_label for key_label in dict_label.keys() if key_label in kk[1][0]]
    label_key = label_keys[0] if label_keys else 'default'

    xpos, ha, s = dict_label[label_key]

    plot.ax.text(xpos, 0.95, '%s'%s, transform=plot.ax.transAxes, ha=ha, va='top', weight='bold')







ax = plot_prof.ax
for nrow, row in df_minmax_prf.loc[df_minmax_prf.iteration == 1, ['nevent', 'min_slot', 'max_slot']].drop_duplicates().reset_index(drop=True).iterrows():
    row_dict = row.to_dict()

    solid_line((row_dict['min_slot'], -0.02), (row_dict['max_slot'] , -0.02))

    avg_slot = 0.5 * (row_dict['min_slot'] + row_dict['max_slot'])

    con = ConnectionPatch(xyA=(nrow, plot_bars_value_0.ax.get_ylim()[1] -0.02 ) ,
                          xyB=(avg_slot,-0.02),
                          coordsA='data', coordsB='data',
                          axesA=plot_bars_value_0.ax, axesB=plot_prof.ax,
                          arrowstyle="<-",
                          connectionstyle="arc,angleA=90,angleB=-90,armA=10,armB=10,rad=0"
                        )
    plot_bars_value_0.ax.add_artist(con)

# arrows second aggregation
ax = plot_bars_res_0.ax
row_dict = row.to_dict()

ax.set_ylim(bottom=-0.1)
solid_line((-plot_bars_res_0.barspace, -0.08), (2 + plot_bars_res_0.barspace, -0.08))

avg_slot = 0

con = ConnectionPatch(#xyA=(nrow, plot_bars_value_1.ax.get_ylim()[1] - 0.1 ) ,
#                      xyB=(1, -0.1),
                      xyA=(0,plot_bars_value_1.ax.get_ylim()[1]), xyB=(1.1,-0.08),
                      coordsA='data', coordsB='data',
                      axesA=plot_bars_value_1.ax, axesB=plot_bars_res_0.ax,
                      arrowstyle="<-",
                      connectionstyle="arc,angleA=90,angleB=-90,armA=10,armB=10,rad=0"
                    )
plot_bars_value_1.ax.add_artist(con)


# arrows connecting axes
for itr in [0]:
    plotA = plt_tot.plotdict[((0,), ('bars_value_res_%d'%itr,), 'StackedGroupedBar')]
    plotB = plt_tot.plotdict[((0,), ('bars_value_%d'%itr,), 'StackedGroupedBar')]
    con = ConnectionPatch(xyA=(1, 0.9), xyB=(1, 0.1),
                          coordsA='axes fraction', coordsB='axes fraction',
                          axesA=plotA.ax, axesB=plotB.ax,
                          arrowstyle="<-",
                          connectionstyle="arc,angleA=50,angleB=-50,armA=20,armB=20,rad=0"
                        )
    plotA.ax.add_artist(con)

for itr in [0,1]:
    plotA = plt_tot.plotdict[((0,), ('bars_value_comp_%d'%itr,), 'StackedGroupedBar')]
    plotB = plt_tot.plotdict[((0,), ('bars_value_%d'%itr,), 'StackedGroupedBar')]
    con = ConnectionPatch(xyA=(0.05, 1), xyB=(0.95, 1),
                          coordsA='axes fraction', coordsB='axes fraction',
                          axesA=plotA.ax, axesB=plotB.ax,
                          arrowstyle="<-",
                          connectionstyle="arc,angleA=140,angleB=40,armA=20,armB=20,rad=0"
                        )
    plotA.ax.add_artist(con)





