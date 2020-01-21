import re
import random
from itertools import combinations, product
from copy import deepcopy
from .topoly_knot import *
from .topoly_homfly import *
from .topoly_lmpoly import *
from .manipulation import check_cuda
from .params import Closure, TopolyException, ReduceMethod
from .polynomial import polynomial as Poly
from .graph import Graph

class AlexanderGraph(Graph):
    name = 'Alexander'

    ### calculations ###
    def invariant(self, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce_method=ReduceMethod.KMT, matrix=False,
                  density=1, level=0, max_cross=15, chirality=False, cuda=True, beg=-1, end=-1, debug=False, run_parallel=False, parallel_workers=None):
        if matrix and cuda and check_cuda():
            return self.alexander_cuda(closure=closure, tries=tries, direction=direction, reduce=reduce_method,
                                       density=density, level=level, debug=debug)
        else:
            return super().invariant(closure, tries, direction, reduce_method, matrix, density, level, max_cross, chirality, cuda, beg, end, debug, run_parallel, parallel_workers)

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_alexander(debug=debug).print_short().split('|')[1].strip())

    def point_alexander(self, debug=False):
        p_red = calc_alexander_poly(self.coordinates_W[0])
        # TODO is it the right condition?
        if not p_red:
            p_red = '1'
        coefs = p_red.split()
        if int(coefs[0]) < 0:
            coefs = [str(-int(_)) for _ in coefs]
        p = Poly('0')
        for k in range(len(coefs)):
            power = k - int((len(coefs)-1)/2)
            p += Poly(coefs[k]) * Poly('x**' + str(power))
        return p

    def alexander_cuda(self, closure=Closure.TWO_POINTS, tries=200, direction=0, reduce=ReduceMethod.KMT,
                       density=1, level=0, debug=False):
        matrix = find_alexander_fingerprint_cuda(self.coordinates_W[0], density, level, closure, tries)
        return matrix


class JonesGraph(Graph):
    name = 'Jones'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_jones(debug=debug).print_short())

    def point_jones(self, debug=False):
        com1 = ''
        com2 = ''
        if debug:
            if self.level > 0:
                for k in range(self.level - 1):
                    com1 += '|  '
                    com2 += '|  '
                com1 += '|->'
                com2 += '|  '
            com1 += self.communicate + self.get_pdcode()
            print(com1)
        # calculating Jones polynomial

        n = self.simplify(debug=debug)  # returns power of x as a result of 1st and 5th Reidemeister move
        if debug:
            print(com2 + "After simplification: " + self.get_pdcode() + '\tn=' + str(n))

        # known cases, to speed up calculations:
        if self.get_pdcode() in self.known.keys() and self.known[self.get_pdcode()]:
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Known case.')
                print(com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 1 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly('1')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + "It's a circle.")
            return res
        if len(self.vertices) == 2 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly('-t**0.5-t**-0.5')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + "It's a split sum of two circles.")
            return res

        # split sum:
        subgraphs = self.create_disjoined_components()
        if len(subgraphs) > 1:
            if debug:
                print(com2 + "It's a split graph.")
                for subgraph in subgraphs:
                    print(subgraph.pdcode)
            self.known[self.get_pdcode()] = Poly('1')
            for k in range(len(subgraphs)):
                subgraph = subgraphs[k]
                subgraph.level = self.level + 1
                subgraph.known = self.known
                subgraph.communicate = ' * '
                res_tmp = subgraph.point_jones(debug=debug)
                self.known = subgraph.known
                self.known[self.get_pdcode()] *= res_tmp
            self.known[self.get_pdcode()] *= Poly('-t**0.5-t**-0.5')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        # crossing reduction:
        if len(self.crossings) > 0:
            # the skein relation
            k = random.randint(0,len(self.crossings)-1)
            sign = self.find_crossing_sign(k)
            if debug:
                print(com2 + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                      str(sign) + " crossing.")
            g1 = self.smooth_crossing(k, sign)
            g1.communicate = str(sign) + '*t^' + str(sign) + '(t^0.5 - t^-0.5)*'
            g1.level += 1
            part1 = g1.point_jones(debug=debug)
            self.known = g1.known

            g2 = self.invert_crossing(k)
            g2.communicate = ' +t^' + str(2*sign) + '* '
            g2.level += 1
            part2 = g2.point_jones(debug=debug)
            self.known = g2.known

            self.known[self.get_pdcode()] = Poly(str(sign)) * Poly('t**0.5-t**-0.5') * Poly('t**' + str(sign)) * part1 + Poly('t**' + str(2*sign)) * part2
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        self.known[self.get_pdcode()] = Poly('1')
        res = Poly('1')  # no crossing, no vertex = empty graph
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res


class HomflyGraph(Graph):
    name = 'HOMFLY-PT'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_homfly(debug=debug))

    def truncate_bytes(s, maxlen=128, suffix=b'...'):
        # type: (bytes, int, bytes) -> bytes
        if maxlen and len(s) >= maxlen:
            return s[:maxlen].rsplit(b' ', 1)[0] + suffix
        return s

    def point_homfly(self, debug=False):
        code = self.emcode.replace(';','\n')
        res = lmpoly(code)
        return res.replace('\n','|')


class YamadaGraph(Graph):
    name = 'Yamada'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_yamada(debug=debug).print_short().split('|')[1].strip())

    def point_yamada(self, max_crossings=10, debug=False):
        com1 = ''
        com2 = ''
        if debug:
            if self.level > 0:
                for k in range(self.level - 1):
                    com1 += '|  '
                    com2 += '|  '
                com1 += '|->'
                com2 += '|  '
            com1 += self.communicate + self.get_pdcode()
            print(com1)
        # calculating Yamada polynomial

        n = self.simplify(debug=debug)  # returns power of x as a result of 1st and 5th Reidemeister move
        if len(self.crossings) > max_crossings:
            raise TopolyException("Too many crossings: {0} limit is {1}".format(str(len(self.crossings)), str(max_crossings)))
        if debug:
            print(com2 + "After simplification: " + self.get_pdcode() + '\tn=' + str(n))

        # known cases, to speed up calculations:
        if self.get_pdcode() in self.known.keys() and self.known[self.get_pdcode()]:
            res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
            if debug:
                print(com2 + 'Known case.')
                print(com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 1 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly(-1) * (
                    Poly('-x-1-x^-1') ** len(set([x.strip() for x in self.vertices[0]])))
            res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
            if debug:
                print(com2 + "It's a bouquet of " + str(
                    len(set([x.strip() for x in
                             self.vertices[0]]))) + " circles.\n" + com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 2 and not self.crossings and len(self.vertices[1]) == 3:
            if set([x.strip() for x in self.vertices[0]]) == set(
                    [x.strip() for x in self.vertices[1]]):  # trivial theta
                self.known[self.get_pdcode()] = Poly('-x^2-x-2-x^-1-x^-2')
                res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
                if debug:
                    print(com2 + "It's a trivial theta.\n" + com2 + "Result " + self.communicate + str(res))
                return res
            elif len(set([x.strip() for x in self.vertices[0]]) & set(
                    [x.strip() for x in self.vertices[1]])) == 1:  # trivial handcuff
                self.known[self.get_pdcode()] = Poly('0')
                res = self.known[self.get_pdcode()]
                if debug:
                    print(com2 + "It's a trivial handcuff graph.\n" + com2 + "Result " + str(res))
                return res

        # other simplifying cases
        for v in range(len(self.vertices)):
            vert = self.vertices[v]
            if len(vert) > 3:
                for k in range(len(vert)):
                    if vert[k] == vert[k - 1]:
                        # bouquet with one loop
                        if debug:
                            print(com2 + "Removing loop.")
                        g = self.remove_loop(v, k)
                        g.level += 1
                        g.communicate = ' * '
                        res_tmp = g.point_yamada(debug=debug)
                        self.known = g.known

                        self.known[self.get_pdcode()] = Poly('-1') * Poly('x+1+x^-1') * res_tmp
                        res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
                        if debug:
                            print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
                        return res

        # split sum:
        subgraphs = self.create_disjoined_components()
        if len(subgraphs) > 1:
            if debug:
                print(com2 + "It's a split graph.")
            self.known[self.get_pdcode()] = Poly('1')
            for k in range(len(subgraphs)):
                subgraph = subgraphs[k]
                subgraph.level = self.level + 1
                subgraph.known = self.known
                subgraph.communicate = ' * '
                res_tmp = subgraph.point_yamada(debug=debug)
                self.known = subgraph.known
                self.known[self.get_pdcode()] *= res_tmp

            res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')

            return res

        # crossing reduction:
        if len(self.crossings) > 0:
            # two ways of removing the crossing.
            g = self.invert_crossing(0)
            g.simplify()
            if len(g.crossings) < len(self.crossings):
                # the skein-like relation
                if debug:
                    print(com2 + "Reducing crossing " + str(self.crossings[0]) + " by skein relation.")
                g1 = self.smooth_crossing(0, 1)
                g1.communicate = ' (x-x^-1)* '
                g1.level += 1
                part1 = g1.point_yamada(debug=debug)
                self.known = g1.known

                g2 = self.smooth_crossing(0, -1)
                g2.communicate = ' -(x-x^-1)* '
                g2.level += 1
                part2 = g2.point_yamada(debug=debug)
                self.known = g2.known

                g3 = self.invert_crossing(0)
                g3.communicate = ' + '
                g3.level += 1
                part3 = g3.point_yamada(debug=debug)
                self.known = g3.known

                self.known[self.get_pdcode()] = Poly('x-x^-1') * (part1 - part2) + part3
                res = Poly(str((-1) ** (n % 2)) + 'x^' + str(n)) * self.known[self.get_pdcode()]
                if debug:
                    print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
                return res
            else:
                # removing the crossing with introduction of new vertex
                if debug:
                    print(com2 + "Reducing crossing " + str(self.crossings[0]) + " by crossing removal.")
                g1 = self.smooth_crossing(0, 1)
                g1.level += 1
                g1.communicate = ' x* '
                part1 = g1.point_yamada(debug=debug)
                self.knonw = g1.known

                g2 = self.smooth_crossing(0, -1)
                g2.level += 1
                g2.communicate = ' +x^-1* '
                part2 = g2.point_yamada(debug=debug)
                self.knonw = g2.known

                g3 = self.smooth_crossing(0, 0)
                g3.level += 1
                g3.communicate = ' + '
                part3 = g3.point_yamada(debug=debug)
                self.knonw = g3.known

                self.known[self.get_pdcode()] = Poly('x') * part1 + Poly('x^-1') * part2 + part3
                res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
                if debug:
                    print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')

                return res

        # edge reduction:
        edges = self.get_noloop_edges()
        if len(edges) > 0:  # then len(graph.vertices) >= 2
            if debug:
                print(com2 + "Reducing noloop edge " + str(edges[0]) + ".")
            g1 = self.remove_edge(edges[0])
            g1.level += 1
            g1.communicate = ''
            part1 = g1.point_yamada(debug=debug)
            self.known = g1.known

            g2 = self.contract_edge(edges[0])
            g2.level += 1
            g2.communicate = ' + '
            part2 = g2.point_yamada(debug=debug)
            self.known = g2.known

            self.known[self.get_pdcode()] = part1 + part2
            res = self.known[self.get_pdcode()] * Poly(str((-1) ** (n % 2)) + 'x^' + str(n))
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        self.known[self.get_pdcode()] = Poly('1')
        res = Poly(str((-1) ** (n % 2)) + 'x^' + str(n))  # no crossing, no vertex = empty graph
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res


class ConwayGraph(Graph):
    name = 'Conway'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_conway(debug=debug).print_short().split('|')[1].strip())

    def point_conway(self, debug=False):
        com1 = ''
        com2 = ''
        if debug:
            if self.level > 0:
                for k in range(self.level - 1):
                    com1 += '|  '
                    com2 += '|  '
                com1 += '|->'
                com2 += '|  '
            com1 += self.communicate + self.get_pdcode()
            print(com1)
        # calculating Jones polynomial

        n = self.simplify(debug=debug)  # returns power of x as a result of 1st and 5th Reidemeister move
        if debug:
            print(com2 + "After simplification: " + self.get_pdcode() + '\tn=' + str(n))

        # known cases, to speed up calculations:
        if self.get_pdcode() in self.known.keys() and self.known[self.get_pdcode()]:
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Known case.')
                print(com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 1 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly('1')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + "It's a circle.")
            return res
        if len(self.vertices) == 2 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly('0')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + "It's a split sum of two circles.")
            return res

        # split sum:
        subgraphs = self.create_disjoined_components()
        if len(subgraphs) > 1:
            if debug:
                print(com2 + "It's a split graph.")
                for subgraph in subgraphs:
                    print(subgraph.pdcode)
            self.known[self.get_pdcode()] = Poly('0')
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        # crossing reduction:
        if len(self.crossings) > 0:
            # the skein relation
            k = random.randint(0, len(self.crossings) - 1)
            sign = self.find_crossing_sign(k)
            if debug:
                print(com2 + "Reducing crossing " + str(self.crossings[k]) + " by skein relation. It is " +
                      str(sign) + " crossing.")
            g1 = self.smooth_crossing(k, sign)
            g1.communicate = str(sign) + 'x*'
            g1.level += 1
            part1 = g1.point_conway(debug=debug)
            self.known = g1.known

            g2 = self.invert_crossing(k)
            g2.communicate = ' + '
            g2.level += 1
            part2 = g2.point_conway(debug=debug)
            self.known = g2.known

            self.known[self.get_pdcode()] = Poly(str(sign)) * Poly('x') * part1 + part2
            res = self.known[self.get_pdcode()]
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        self.known[self.get_pdcode()] = Poly('1')
        res = Poly('1')  # no crossing, no vertex = empty graph
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res


class KauffmanBracketGraph(Graph):
    name = 'Kauffman bracket'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_kauffman_bracket(debug=debug).print_short().split('|')[1].strip())

    def point_kauffman_bracket(self, B='A**-1', d='-A**2-A**-2', debug=False):
        # calculating Kaufman Bracket polynomial

        res = Poly('0')
        n = len(self.crossings)
        for state in product([-1,1],repeat=n):
            a = int((n + sum(state))/2)
            b = int((n - sum(state))/2)
            g = deepcopy(self)
            for smooth in state:
                g = g.smooth_crossing(0,smooth)
            parta = Poly('A**' + str(a))
            partb = Poly('B**' + str(b))
            partd = Poly('d**' + str(len(g.vertices)-1))
            res += parta * partb * partd
        res = res({'B': B, 'd': d})
        return res


class WritheGraph(Graph):
    name = 'Writhe'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_writhe(debug=debug))

    def point_writhe(self, debug=False):
        res = sum([self.find_crossing_sign(k) for k in range(len(self.crossings))])
        return res


class KauffmanPolynomialGraph(WritheGraph):
    name = 'Kauffman polynomial'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_kauffman_polynomial(debug=debug).print_short())

    def point_kauffman_polynomial(self, debug=False):
        n = self.simplify(debug=debug)
        l = self.point_writhe()
        res = Poly('a**' + str(-l))
        res *= self.KauffmanPolynomial_L(debug=debug)
        return res

    def KauffmanPolynomial_L(self, debug=False):
        com1 = ''
        com2 = ''
        if debug:
            if self.level > 0:
                for k in range(self.level - 1):
                    com1 += '|  '
                    com2 += '|  '
                com1 += '|->'
                com2 += '|  '
            com1 += self.communicate + self.get_pdcode()
            print(com1)
        # calculating Yamada polynomial

        n = int(self.simplify(debug=debug)/2)  # returns power of x as a result of 1st and 5th Reidemeister move
        if debug:
            print(com2 + "After simplification: " + self.get_pdcode() + '\tn=' + str(n))

        # known cases, to speed up calculations:
        if self.get_pdcode() in self.known.keys() and self.known[self.get_pdcode()]:
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + 'Known case.')
                print(com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 1 and not self.crossings:  # bouquet of circles:
            # number of circles in bouquet = len(set(graph.vertices[0]))
            self.known[self.get_pdcode()] = Poly(1)
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + "It's a bouquet of " + str(
                    len(set([x.strip() for x in
                             self.vertices[0]]))) + " circles.\n" + com2 + "Result " + self.communicate + str(res))
            return res
        if len(self.vertices) == 2 and not self.crossings:
            self.known[self.get_pdcode()] = Poly('a+a**-1-z') * Poly('z**-1')
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + "It's a split sum of two circles.\n" + com2 + "Result " + self.communicate + '(' + str(res) + ')')
            return res

        # split sum:
        subgraphs = self.create_disjoined_components()
        if len(subgraphs) > 1:
            if debug:
                print(com2 + "It's a split graph.")
            self.known[self.get_pdcode()] = Poly('1')
            for k in range(len(subgraphs)):
                subgraph = subgraphs[k]
                subgraph.level += 1
                subgraph.known = self.known
                subgraph.communicate = ' * '
                res_tmp = subgraph.KauffmanPolynomial_L(debug=debug)
                self.known = subgraph.known
                self.known[self.get_pdcode()] *= res_tmp
            self.known[self.get_pdcode()] *= Poly('a+a**-1-z')*Poly('z**-1')
            res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
            if debug:
                print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
            return res

        # crossing reduction:
        if len(self.crossings) > 0:
            # two ways of removing the crossing.
            g = self.invert_crossing(0)
            g.simplify()
            if len(g.crossings) < len(self.crossings):
                # the skein-like relation
                if debug:
                    print(com2 + "Reducing crossing " + str(self.crossings[0]) + " by skein relation.")
                g1 = self.smooth_crossing(0, 1)
                g1.communicate = ' z* '
                g1.level += 1
                part1 = g1.KauffmanPolynomial_L(debug=debug)
                self.known = g1.known

                g2 = self.smooth_crossing(0, -1)
                g2.communicate = ' +z* '
                g2.level += 1
                part2 = g2.KauffmanPolynomial_L(debug=debug)
                self.known = g2.known

                g3 = self.invert_crossing(0)
                g3.communicate = ' - '
                g3.level += 1
                part3 = g3.KauffmanPolynomial_L(debug=debug)
                self.known = g3.known

                self.known[self.get_pdcode()] = Poly('z') * (part1 + part2) - part3
                res = self.known[self.get_pdcode()] * Poly('a^' + str(n))
                if debug:
                    print(com2 + 'Result ' + str(res) + '\t(n=' + str(n) + ').')
                return res

        self.known[self.get_pdcode()] = Poly('1')
        res = self.known[self.get_pdcode()]  # no crossing, no vertex = empty graph
        if debug:
            print(com2 + "Empty graph. Result " + str(res))
        return res


class BlmhoGraph(KauffmanPolynomialGraph):
    name = 'BLM/Ho'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_blmho(debug=debug).print_short())

    def point_blmho(self, debug=False):
        res = self.KauffmanPolynomial_L(debug=debug)
        res = res({'a': 1, 'z': 'x'})
        if debug:
            print('After substitution: ' + str(res))
        return res


class ApsGraph(Graph):
    name = 'APS'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_aps(debug=debug).print_short())

    def point_aps(self, debug=False):
        raise NotImplementedError('APS not implemented yet!')

class GlnGraph(Graph):
    name = 'GLN'

    def calc_point(self, g, debug):
        return __class__.name + ': ' + str(g.point_gln(debug=debug).print_short())

    def point_gln(self, debug=False):
        raise NotImplementedError('GLN not implemented yet!')
