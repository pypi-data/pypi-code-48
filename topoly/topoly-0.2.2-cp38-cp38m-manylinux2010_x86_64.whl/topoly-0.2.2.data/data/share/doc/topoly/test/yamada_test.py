#!/usr/bin/python3
from time import time

from topoly import import_coords, yamada, homfly, alexander, conway, \
    jones, yamada, blmho, kauffman_bracket, kauffman_polynomial, Closure, TopolyException
#yamada, homfly, alexander, conway,
algos = [yamada, alexander, conway, jones, blmho, kauffman_bracket, kauffman_polynomial]

# with open('/Users/pawel/Downloads/2efv.pdb', 'r') as myfile:
# with open('/Users/pawel/Downloads/1aoc.pdb', 'r') as myfile:
# with open('/Users/pawel/PycharmProjects/topoly/structures/31.xyz', 'r') as myfile:
# with open('/Users/pawel/Downloads/1j85.pdb', 'r') as myfile:
# with open('/Users/pawel/Downloads/mathematica.xyz', 'r') as myfile:
#file = 'data/1j85.pdb'
file = 'data/2efv.xyz'
with open(file, 'r') as myfile:
    data = myfile.read()
#curve = import_coords(data, format='PDB')
curve = import_coords(data)
#print(curve)
for algo in algos:
    try:
        t0 = time()
        print(algo.__name__, ' : ', algo(curve, matrix=True, closure=Closure.TWO_POINTS, tries=10, matrix_plot=True,
                                         output_file=algo.__name__+'.txt', plot_ofile=algo.__name__, translate=True,
                                         run_parallel=True, parallel_workers=None))
        t = time()-t0
        print('Done {0} in {1} s.'.format(algo.__name__, round(t, 3)))
    except TopolyException as ve:
        print(algo.__name__, ' : ' + str(ve))


# g = Graph(code)
# for key in g.abstract_graph:
#     print(key,g.abstract_graph[key])
# print(g.find_loops())
#     print('Alexander ', alexander(curve, closure_method='two_points', translate=True, matrix=True, tries=20))
    # print('Alexander ', alexander(curve, closure_method='two_points', translate=True, beg=6, end=15, tries=20))
    # print('Conway ' + str(k), conway(curve, closure_method='closed', translate=True))
    # print('Jones ' + str(k), jones(curve, closure_method='closed', translate=True))
    # print('HOMFLY ' + str(k), homfly(curve, closure_method='closed', translate=True))
    # print('Yamada ' + str(k), yamada(curve, closure_method='closed', translate=True))
    # print('BLM/Ho ' + str(k), blmho(curve, closure_method='closed', translate=True))
    # print('Kauffman bracket ' + str(k), kauffman_bracket(curve, closure_method='closed', translate=True))
    # print('Kauffman polynomial ' + str(k), kauffman_polynomial(curve, closure_method='closed', translate=True))
    # k += 1

