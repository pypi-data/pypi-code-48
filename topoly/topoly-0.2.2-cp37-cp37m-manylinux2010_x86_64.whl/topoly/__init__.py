#!/usr/bin/python3
"""
The main module collecting the functions designed for the users.

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

from .manipulation import *
from .invariants import *
from .topoly_knot import *
from .codes import *
from .plotting import KnotMap, Reader
from .graph_impl import *
from .params import Closure, ReduceMethod, PlotFormat, TopolyException
from .polygongen import *
### invariants
def alexander(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, AlexanderGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def conway(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, ConwayGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def jones(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, JonesGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def homfly(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, HomflyGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def yamada(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, YamadaGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def kauffman_bracket(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, KauffmanBracketGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def kauffman_polynomial(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, KauffmanPolynomialGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def blmho(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, BlmhoGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end, max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def aps(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1, max_cross=15, chirality=False,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, ApsGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,  max_cross=max_cross, chirality=chirality,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def gln(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, GlnGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)

def writhe(input_data,
           closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT,
           poly_reduce=True, translate=False, beg=-1, end=-1,
           matrix=False, density=1, level=0, matrix_plot=False, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG,
           output_file='', cuda=True, debug=False, run_parallel=False, parallel_workers=None):
    return calculate_invariant(input_data, WritheGraph,
            closure=closure, tries=tries, direction=direction, reduce_method=reduce_method,
            poly_reduce=poly_reduce, translate=translate, beg=beg, end=end,
            matrix=matrix, density=density, level=level, matrix_plot=matrix_plot, plot_ofile=plot_ofile,
            plot_format=plot_format, output_file=output_file, cuda=cuda, debug=debug, run_parallel=run_parallel, parallel_workers=parallel_workers)


### sampling
## polygongen - Bartek
def generate_curve(n):
    return

def generate_loop(n, equilateral=False):
    return

def generate_lasso(looplength, taillength, no_of_structures,
                   is_loop_closed = False, print_with_index = True,
                   file_prefix = 'lasso', folder_prefix = '', out_fmt= (3,3,5)):
    return Polygons(looplength, taillength, no_of_structures, is_loop_closed,
                    print_with_index, file_prefix, folder_prefix, out_fmt)

## /
#TODO Kod do zintegrowania - Paweł D.
def find_loops(curve):
    g = Graph(curve)
    return g.find_loops()

def find_thetas(curve):
    g = Graph(curve)
    return g.find_thetas()

## /

#def find_handcuffs(curve):
#    return

#TODO surfaces - zintegrować z topoly_surfaces.pyx - Bartek
#TODO Wanda - sprawdzić czy funkcja może stworzyć samą powierzchnię
def make_surface(coordinates):
    return

#TODO surfaces - zintegrować z topoly_surfaces.pyx - Bartek
def lasso_type(coordinates, bindex, eindex):
    # TODO add calculation of whole fingerprint
    return

#TODO surfaces - zintegrować z topoly_surfaces.pyx - Bartek
def lasso_classify(coordinates, loop_indices):
    return

#TODO Integracja BioPython - wyciągnąć mostki z CIF/PDB

#TODO - Bartek + Wanda + Pol - smoothowanie do funkcji lassowych

#TODO - wystawić funkcję z topoly_surfaces - BARTEK
## /



### translating/understanding
#TODO - Paweł D. - podpiąć kod z wnętrza topoly
def translate(code, outtype):
    g = Graph(code)
    if outtype == 'PD':
        return g.pdcode
    elif outtype == 'EM':
        return g.emcode
    else:
        raise NameError('Unknown or unhandled yet type of output code.')
        return

def find_matching(data):
    return find_matching_structure(data)


def plot_matrix(matrix, plot_ofile="KnotFingerPrintMap", plot_format=PlotFormat.PNG, matrix_type="knot", circular=False,
                 yamada=False, cutoff=0.48, debug=False, disk=True):
    return manipulation.plot_matrix(matrix, plot_ofile=plot_ofile, plot_format=plot_format, matrix_type=matrix_type, circular=circular,
                                    yamada=yamada, cutoff=cutoff, debug=debug, disk=disk)

#TODO przekleić z klasy graph - Paweł D. - dodalem, jeszcze brak testu.
def plot_graph(code):
    g = Graph(code)
    g.plot()
    return

### importing code/coordinates
# TODO - Paweł R. - użyć BioPythona, CIF, PDB
def import_coords(input_data, format=None, pipe=False):
    if format and format.lower() not in InputData.list_formats():
        raise AttributeError('The chosen format not supported (yet?). The available formats: ' + str(InputData.list_formats()))
    if type(input_data) is str and (len(input_data.splitlines()) > 1 or '"' in input_data):
        pipe = True
    if pipe:
        data = input_data
    else:
        with open(input_data, 'r') as myfile:
            data = myfile.read()
    return InputData.read_format(data, format)

#TODO - zwróć z pliku 'codes.py' - Paweł D. - test....
def import_structure(name):
    if name in PD.keys():
        return Graph(PD[name])
    else:
        raise NameError('The structure chosen is not available in the local library.')


### structure manipulation
#TODO - dokończyć - wystawić z kodu Wandy... - Paweł D. - wytawione, musze sprawdzic dzialanie
def reduce(curve, method=None, closed=True):
    return chain_reduce(curve, method, closed=closed)

def kmt(curve, closed=True):
    return chain_kmt(curve, closed)

def reidemeister(curve):
    return chain_reidemeister(curve)

#TODO - podłączyć do close_chain w topoly_preprocess - Wanda - Sorry, to juz chyba bylo w manipulation [Pawel]
def close_curve(chain, method=Closure.TWO_POINTS, direction=0):
    return chain_close(chain, method, direction)