"""
The module containing the functions for calculating the isotopy invariants starting from graphs. In particular,
it contains functions to calculate knot invariants (Jones, Alexander, HOMFLY-PT) and spatial graph invariants.

Pawel Dabrowski-Tumanski
p.dabrowski at cent.uw.edu.pl
04.09.2019

Docs:
https://realpython.com/documenting-python-code/#docstring-types

The type used here: Google


Support in PyCharm:
https://www.jetbrains.com/help/pycharm/settings-tools-python-integrated-tools.html
- change default reStructuredText to Google

Docs will be published in: https://readthedocs.org/

"""

import array
from .topoly_homfly import *
from .topoly_preprocess import *
from .topoly_knot import *
from .topoly_lmpoly import *
from .graph import Graph
from .polvalues import polvalues
from . import plot_matrix, data2Wanda
from .params import Closure, ReduceMethod, PlotFormat

knot_amount = 40

# general function
def calculate_invariant(input_data, invariant,
            closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
            poly_reduce=True, translate=False,
            matrix=False, density=1, level=0, beg=-1, end=-1, max_cross=15, chirality=False,
            matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG, disk=False,
            output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):

    if disk:
        matrix_plot = True
    if matrix_plot:
        matrix = True
    if isinstance(input_data, invariant):
        g = input_data
    else:
        g = invariant(input_data)
    result = g.invariant(closure=closure, tries=tries, direction=direction, cuda=cuda,
                         reduce_method=reduce_method, matrix=matrix, density=density, beg=beg, end=end,
                         max_cross=max_cross, chirality=chirality, level=level, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

    # macierz liczona programem Wandy to string, z nazwami wezlow podanymi explicite. Jesli bylo inaczej, to musimy
    # przetlumaczyc wielomiany wezlow do macierzy.
    if type(result) is not str:
        if translate:
            result = find_matching_structure(result)
        elif not poly_reduce:
            result = make_poly_explicit(result)    # TODO place it somewhere
    if matrix_plot:
        plot_matrix(result, plot_ofile=plot_ofile, plot_format=plot_format, disk=disk)
    if output_file:
        # TODO - fix writing results to file...
        with open(output_file, 'w') as myfile:
            myfile.write(str(result))
        with open(output_file + '_wanda.txt', 'w') as myfile:
            myfile.write(data2Wanda(result, 1, -1))
    return result


def find_matching_structure(data):
    if not data:
        return '0_1'
    if len(data) == 0:
        return data
    elif type(list(data.keys())[0]) is str:
        to_del = list(data.keys())
        for prob in to_del:
            res = find_point_matching({prob.split(':')[0].strip(): prob.split(':')[1].strip()})
            data[res] = data[prob]
        for e in to_del:
            data.pop(e)
    else:
        for key in data.keys():
            to_del = list(data[key].keys())
            for prob in to_del:
                res = find_point_matching({prob.split(':')[0].strip(): prob.split(':')[1].strip()})
                data[key][res] = data[key][prob]
            for e in to_del:
                data[key].pop(e)
    return data


def find_point_matching(data):
    possible = []
    for key in data.keys():
        d = polvalues[key]
        #TODO clean it
        if '{' not in data[key] and '|' not in data[key] and '[' not in data[key] and 'Too' not in data[key]:
            v = ' '.join([str(-int(_)) for _ in data[key].strip().split()])
        else:
            v = -1
        if data[key] in d.keys():
            res = d[data[key]].split('|')
        elif v in d.keys():
            res = d[v].split('|')
        else:
            return 'Unknown polynomial values (' + str(key) + ' ' + str(data[key]) + ').'
        if not possible:
            possible = res
        else:
            possible = set(possible) & set(res)
    return '|'.join(possible)
