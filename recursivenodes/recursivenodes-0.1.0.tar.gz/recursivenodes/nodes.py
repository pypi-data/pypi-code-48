"""Node sets for the `d`-simplex implemented by ``recursivenodes``"""

import numpy as np

from recursivenodes.utils import npolys, multiindex_equal, multiindex_up_to, coord_map
from recursivenodes.quadrature import gaussjacobi, lobattogaussjacobi
from recursivenodes.polynomials import proriolkoornwinderdubinervandermonde

def equispaced(d, n, domain='biunit'):
    '''Equispaced nodes for polynomials up to degree `n` on the `d`-simplex.

    Args:
        d (int): The dimension of the simplex.
        n (int): The polynomial degree
        domain (str, optional) -- The domain of the simplex.  See ":ref:`domains`" for the choices and their formal definitions.

    Returns:
        ndarray: Equispaced nodes as a 2D array with one row for each of
        `\\binom{n+d}{d}` nodes, and `d` columns for coordinates (or `d+1`
        if ``domain='barycentric'``).

    Example:

        .. plot::
           :include-source: True

           >>> import matplotlib.pyplot as plt
           >>> from numpy import eye
           >>> from recursivenodes.nodes import equispaced
           >>> from recursivenodes.utils import coord_map
           >>> nodes = equispaced(2, 7, domain='equilateral')
           >>> corners = coord_map(eye(3), 'barycentric', 'equilateral')
           >>> plt.plot(corners[[0,1,2,0],0], corners[[0,1,2,0],1])
           [<matplotlib.lines.Line2D object at ...>]
           >>> plt.scatter(nodes[:,0], nodes[:,1])
           <matplotlib.collections.PathCollection object at ...>
           >>> plt.gca().set_aspect('equal')
           >>> plt.title('Equispaced Nodes')
           Text(0.5, 1.0, 'Equispaced Nodes')
           >>> plt.show()
    '''
    N = npolys(d, n)
    x = np.ndarray((N, d))
    for (k, i) in enumerate(multiindex_up_to(d, n)):
        x[k, :] = np.array(i) / n
    return coord_map(x, 'unit', domain)


def equispaced_interior(d, n, domain='biunit'):
    '''Equispaced nodes for polynomials up to degree `n` on the `d`-simplex,
    all of which are in the interior.

    Args:
        d (int): The dimension of the simplex.
        n (int): The polynomial degree
        domain (str, optional): The domain of the simplex.  See ":ref:`domains`" for the choices and their formal definitions.

    Returns:
        ndarray: Equispaced interior nodes as a 2D array with one row for each of
        `\\binom{n+d}{d}` nodes, and `d` columns for coordinates (or `d+1`
        if ``domain='barycentric'``).

    Example:

        .. plot::
           :include-source: True

           >>> import matplotlib.pyplot as plt
           >>> from numpy import eye
           >>> from recursivenodes.nodes import equispaced_interior
           >>> from recursivenodes.utils import coord_map
           >>> nodes = equispaced_interior(2, 7, domain='equilateral')
           >>> corners = coord_map(eye(3), 'barycentric', 'equilateral')
           >>> plt.plot(corners[[0,1,2,0],0], corners[[0,1,2,0],1])
           [<matplotlib.lines.Line2D object at ...>]
           >>> plt.scatter(nodes[:,0], nodes[:,1])
           <matplotlib.collections.PathCollection object at ...>
           >>> plt.gca().set_aspect('equal')
           >>> plt.title('Equispaced Interior Nodes')
           Text(0.5, 1.0, 'Equispaced Interior Nodes')
           >>> plt.show()
    '''
    N = npolys(d, n)
    x = np.ndarray((N, d))
    for (k, i) in enumerate(multiindex_up_to(d, n)):
        x[k, :] = (np.array(i) + 1/(d+1)) / (n+1)
    return coord_map(x, 'unit', domain)


def blyth_luo_pozrikidis(d, n, x=None, domain='biunit'):
    '''Create Blyth-Luo-Pozrikidis nodes from a 1D node set for polynomials up
    to degree `n` on the `d`-simplex.

    Notes:

        The Blyth-Luo-Pozrikidis rule places an interior node with multi-index
        `\\alpha` at the barycentric point `\\boldsymbol{b}(\\alpha)` such that

        .. math::
           :label: blp

           b_i(\\alpha) = x^n_{\\alpha_i} + \\frac{1}{d}(1 - \\sum_{j\\neq i} x^n_{\\alpha_j}).

        Points on the boundary look like `(d-1)`-simplex Blyth-Luo-Pozrikidis nodes.

    Args:
        d (int): The dimension of the simplex.
        n (int): The polynomial degree
        x (ndarray, optional): 1D node set on `[0, 1]` with `n+1` points.  Lobatto-Gauss-Legendre nodes are used if  ``x=None``.
        domain (str, optional): The domain of the simplex.  See ":ref:`domains`" for the choices and their formal definitions.

    Returns:
        ndarray: Blyth-Luo-Pozrikidis nodes as a 2D array with one row for each of
        `\\binom{n+d}{d}` nodes, and `d` columns for coordinates (or `d+1`
        if ``domain='barycentric'``).

    Example:

        This plot shows the Blyth-Luo-Pozrikidis nodes with lines connecting the
        Lobatto-Gauss-Legendre nodes on the edges.  The definition in :eq:`blp` is
        designed to place the nodes in the centroids of the triangles created by the
        intersecting lines.

        .. plot::
           :include-source: True

           >>> import matplotlib.pyplot as plt
           >>> from numpy import eye
           >>> from recursivenodes.nodes import blyth_luo_pozrikidis
           >>> from recursivenodes.utils import coord_map, multiindex_equal
           >>> nodes = blyth_luo_pozrikidis(2, 7, domain='equilateral')
           >>> corners = coord_map(eye(3), 'barycentric', 'equilateral')
           >>> # plot grid lines
           >>> for (i, al) in enumerate(multiindex_equal(3, 7)):
           ...     if min(al) > 0 or max(al) == sum(al): continue
           ...     for (j, be) in enumerate(multiindex_equal(3, 7)):
           ...         if j <= i or min(be) > 0 or max(be) != max(al) or sum(be) != sum(al): continue
           ...         for d in range(3):
           ...             if al[d] == be[d] and al[d] != 0:
           ...                 _ = plt.plot(nodes[[i,j],0], nodes[[i,j],1], linestyle='--', c='grey')
           >>> plt.plot(corners[[0,1,2,0],0], corners[[0,1,2,0],1])
           [<matplotlib.lines.Line2D object at ...>]
           >>> plt.scatter(nodes[:,0], nodes[:,1])
           <matplotlib.collections.PathCollection object at ...>
           >>> plt.gca().set_aspect('equal')
           >>> plt.title('Blyth-Luo-Pozrikidis Nodes')
           Text(0.5, 1.0, 'Blyth-Luo-Pozrikidis Nodes')
           >>> plt.show()

    References:

        :cite:`BlPo06,LuPo06`
    '''
    if x is None:
        x = coord_map(lobattogaussjacobi(n+1)[0], 'biunit', domain)
    n = len(x) - 1
    y = coord_map(x, domain, 'unit')
    N = npolys(d, n)
    xd = np.zeros((N, d))
    k = 0
    for (k, i) in enumerate(multiindex_equal(d+1, n)):
        numzero = sum([int(y[l] == 0.) for l in i])
        weight = 0.
        for j in range(d+1):
            ibutj = i[0:j] + i[(j+1):]
            yibutj = [y[l] for l in ibutj]
            thisnumzero = sum([int(z == 0) for z in yibutj])
            if thisnumzero < numzero: continue
            yj = 1. - sum(yibutj)
            weight += 1
            for l in range(j):
                if (l < d):
                    xd[k, l] += y[i[l]]
            if (j < d):
                xd[k, j] += yj
            for l in range(j+1, d+1):
                if (l < d):
                    xd[k, l] += y[i[l]]
        xd[k,:] /= weight
    return coord_map(xd, 'unit', domain)


def _warburton_b(d, xt, i):
    b = np.ones((xt.shape[0], 1))
    tol = 1.e-8
    bdry = np.zeros(b.shape)
    for j in range(d+1):
        if j == i:
            continue
        nonzero = np.abs(2. * xt[:, j] + xt[:, i]) > tol
        b[nonzero, 0] *= (2. * xt[nonzero, j]) / (2. * xt[nonzero, j] + xt[nonzero, i])
        bdry[~nonzero, 0] += 1.
    isbdry = bdry[:, 0] > 0.
    if d == 2:
        ''' The implementation of warp and blend, evident in the Lebesgue constants
        in the paper and in modepy (https://github.com/inducer/modepy/blob/master/modepy/nodes.py)
        uses the blending scaling (2 * l2) * (2 * l3) / (1. - (l2 - l3)**2) instead of
        (2 * l2) * (2 * l3) / ((2 * l2 + l1)*(2 * l3 + l1)).

        If l1 + l2 + l3 = 1, this is equivalent, because

        (1. - (l2 - l3)**2) = (1. + (l2 - l3))*(1. - (l2 - l3))
                            = (l1+l2+l3 +l2-l3)*(l1+l2+l3 -l2+l3)=(2*l2+l1)*(2.*l3+l1)

        BUT, when we are blending for higher dimensions, we may be using a subset of
        barycentric coordinates, i.e. l1 + l2 + l3 + l4 = 1, l4 > 0, and we are computing
        a face warp for the l4 face, so we use only the (l1,l2,l3) coordinate.  In this case
        l1+l2+l3 != 1, so the two blending scalings are not equivalent.  I'm choosing
        to follow the implementation so that I can reproduce the computed Lebesgue constants.'''
        i2 = (i + 1) % 3
        i3 = (i + 2) % 3
        b[~isbdry, 0] = 4. * xt[~isbdry, i2] * xt[~isbdry, i3] \
                        / (1. - (xt[~isbdry, i2]-xt[~isbdry, i3])**2)
    b[isbdry, 0] = 1. / (bdry[isbdry, 0] + 1.)
    return b


def _warburton_g(d, n, xt, alpha=0., x=None):
    g = np.zeros(xt.shape)
    if (d == 1):
        if x is None:
            x, _ = lobattogaussjacobi(n+1)
        xe = np.linspace(-1., 1., n+1, endpoint=True)
        diff = (x - xe) / 2
        V = proriolkoornwinderdubinervandermonde(1, n, xe.reshape((n+1, 1)))
        P = np.linalg.solve(V, diff)
        T = proriolkoornwinderdubinervandermonde(1, n, xt[:, [0]] - xt[:, [1]])
        g[:, 0] = T.dot(P)
        g[:, 1] = -g[:, 0]
    else:
        for i in range(d+1):
            rem = [j for j in range(d+1) if j != i]
            gi = _warburton_g(d-1, n, xt[:, rem], alpha, x)
            bi = _warburton_b(d, xt, i)
            g[:, rem] += (1. + (alpha * xt[:, [i]])**2) * gi * bi
    return g


#: A dictionary of optimal values of the blending parameter `\alpha` computed
#: in :cite:`Warb06`.  Keyed by ``(d, n)`` tuples.
#: 
#: Example:
#:     >>> warburton_alpha[(2,7)]
#:     1.0999
warburton_alpha = {
    (2, 3):  1.4152, (3, 3):  0.0000,
    (2, 4):  0.1001, (3, 4):  0.1002,
    (2, 5):  0.2751, (3, 5):  1.1332,
    (2, 6):  0.9808, (3, 6):  1.5608,
    (2, 7):  1.0999, (3, 7):  1.3413,
    (2, 8):  1.2832, (3, 8):  1.2577,
    (2, 9):  1.3648, (3, 9):  1.1603,
    (2, 10): 1.4773, (3, 10): 1.0153,
    (2, 11): 1.4959, (3, 11): 0.6080,
    (2, 12): 1.5743, (3, 12): 0.4523,
    (2, 13): 1.5770, (3, 13): 0.8856,
    (2, 14): 1.6223, (3, 14): 0.8717,
    (2, 15): 1.6258, (3, 15): 0.9655,
}


def warburton(d, n, x=None, alpha=None, domain='biunit'):
    '''Warburton *warp & blend* nodes from a 1D node set for polynomials up
    to degree `n` on the `d`-simplex.

    Notes:

        The Warburton *warp & blend* nodes define a node's coordinates as a
        displacement from equispaced coordinates by blending together
        distortion maps of the `d`-simplex that warp the edge nodes
        to match the 1D node set.  One optimization parameter `\\alpha`
        controls the blending in the interior of the simplex.

    Args:
        d (int): The dimension of the simplex.
        n (int): The polynomial degree
        x (ndarray, optional): 1D node set on `[0, 1]` with `n+1` points.  Lobatto-Gauss-Legendre nodes are used if ``x=None``.
        alpha (float, optional): The blending parameter. If ``alpha=None``, a precomputed optimal parameter is used if known.
        domain (str, optional): The domain of the simplex.  See ":ref:`domains`" for the choices and their formal definitions.

    Returns:
        ndarray: Warburton *warp & blend* nodes as a 2D array with one row for each of
        `\\binom{n+d}{d}` nodes, and `d` columns for coordinates (or `d+1`
        if ``domain='barycentric'``).

    Example:

        .. plot::
           :include-source: True

           >>> import matplotlib.pyplot as plt
           >>> from numpy import eye
           >>> from recursivenodes.nodes import warburton
           >>> from recursivenodes.utils import coord_map
           >>> nodes = warburton(2, 7, domain='equilateral')
           >>> corners = coord_map(eye(3), 'barycentric', 'equilateral')
           >>> plt.plot(corners[[0,1,2,0],0], corners[[0,1,2,0],1])
           [<matplotlib.lines.Line2D object at ...>]
           >>> plt.scatter(nodes[:,0], nodes[:,1])
           <matplotlib.collections.PathCollection object at ...>
           >>> plt.gca().set_aspect('equal')
           >>> plt.title('Warburton Warp & Blend Nodes')
           Text(0.5, 1.0, 'Warburton Warp & Blend Nodes')
           >>> plt.show()

    References:

        :cite:`Warb06`
    '''
    if not (x is None):
        x = coord_map(x, domain, 'biunit')
    if alpha is None:
        try:
            alpha = warburton_alpha[(d, n)]
        except KeyError:
            alpha = 0.
    xt = equispaced(d, n, domain='barycentric')
    g = _warburton_g(d, n, xt, alpha, x)
    xt += g
    return coord_map(xt, 'barycentric', domain)


class NodeFamily:
    ''' Family of nodes on the unit interval.  This class essentially is a lazy-evaluate-and-cache dictionary: the user passes a routine to evaluate entries for unknown keys '''

    def __init__(self, f):
        self._f = f
        self._cache = {}

    def __getitem__(self, key):
        try:
            return self._cache[key]
        except KeyError:
            value = self._f(key)
            self._cache[key] = value
            return value


# For each family, family[n] should be a a set of n+1 points in [0,1] in increasing order that is symmetric about 1/2,
# family[n] should be None if the family does not have a representative for that index
#
# We predefine:
#
#   - shifted Lobatto-Gauss-Legendre  (lgl_family)
#   - shifted Lobatto-Gauss-Chebyshev (lgc_family)
#   - shifted Gauss-Legendre          (gl_family)
#   - shifted Gauss-Chebyshev         (gc_family)
#   - equispaced, including endpoints (equi_family)
#   - equispaced, interior            (equi_interior_family)
lgl_family = NodeFamily(lambda n: coord_map(lobattogaussjacobi(n+1)[0], 'biunit', 'unit') if n > 0 else None)
lgc_family = NodeFamily(lambda n: coord_map(lobattogaussjacobi(n+1, -0.5, -0.5)[0], 'biunit', 'unit') if n > 0 else None)
gl_family = NodeFamily(lambda n: coord_map(gaussjacobi(n+1)[0], 'biunit', 'unit') if n >= 0 else None)
gc_family = NodeFamily(lambda n: coord_map(gaussjacobi(n+1, -0.5, -0.5)[0], 'biunit', 'unit') if n >= 0 else None)
equi_family = NodeFamily(lambda n: np.linspace(0., 1., n+1) if n > 0 else None)
equi_interior_family = NodeFamily(lambda n: np.linspace(
    0.5/(n+1), 1.-0.5/(n+1), n+1) if n >= 0 else None)


def _recursive(d, n, alpha, family):
    '''The barycentric d-simplex coordinates for a
    multiindex alpha with length n, based on a 1D node family.'''
    xn = family[n]
    b = np.zeros((d,))
    if xn is None:
        return b
    if d == 2:
        b[:] = xn[[alpha[0],alpha[1]]] 
        return b
    weight = 0.
    for i in range(d):
        alpha_noti = alpha[:i] + alpha[i+1:]
        n_noti = n - alpha[i]
        w = xn[n_noti]
        br = _recursive(d-1, n_noti, alpha_noti, family)
        b[:i] += w * br[:i]
        b[i+1:] += w * br[i:]
        weight += w
    b /= weight
    return b


def _decode_family(family):
    if family is None:
        family = lgl_family
    elif isinstance(family, str):
        if family == 'lgl':
            family = lgl_family
        elif family == 'lgc':
            family = lgc_family
        elif family == 'gl':
            family = gl_family
        elif family == 'gc':
            family = gc_family
        elif family == 'equi':
            family = equi_family
        elif family == 'equi_interior':
            family = equi_interior_family
    elif isinstance(family, tuple) and len(family) == 2 and family[0] == 'lgg':
        a = family[1]
        family = NodeFamily(lambda n: coord_map(lobattogaussjacobi(n+1, a-0.5, a-0.5)[0], 'biunit', 'unit') if n > 0 else None)
    elif isinstance(family, tuple) and len(family) == 2 and family[0] == 'gg':
        a = family[1]
        family = NodeFamily(lambda n: coord_map(gaussjacobi(n+1, a-0.5, a-0.5)[0], 'biunit', 'unit') if n >= 0 else None)
    return family


def recursive(d, n, family='lgl', domain='barycentric'):
    '''Recursively defined nodes for `\\mathcal{P}_n(\\Delta^d)`, the polynomials
    with degree at most `n` on the `d`-simplex, based on a 1D node family.

    Notes:

        Some definitions:

        - A 1D *node family* is a collection `\\{\\boldsymbol{x}^k\\}` of 1D node sets
          for every degree `k`.

        - A 1D *node set* `\\boldsymbol{x}^k=(x^k_0, \\dots, x^k_k)` is a sorted list
          of `k+1` points in `[0,1]` that is symmetric about `1/2`.

        - The `barycentric triangle`_ is a canonical domain for the `d`-simplex in
          `\\mathbb{R}^{d+1}`: positive coordinates `\\boldsymbol{b}
          = (b_0, b_1, \\dots b_d)` such that `\\sum_i b_i = 1`.

        - For a multi-index_ `\\alpha`, let `\\#\\alpha` be its length,
          `|\\alpha|` its sum, and `\\alpha_{\\backslash i}` the multi-index
          created by removing `\\alpha_i`: nodes that define a basis of
          `\\mathcal{P}_n(\\Delta^d)` can be indexed by `\\alpha` such that
          `\\#\\alpha = d+1` and `|\\alpha| = n`.

        - `I^d_i` is the map from `\\mathbb{R}^{d-1}` to `\\mathbb{R}^d`
          that inserts a zero for the `i`-th coordinate.

        The recursive definition of barycentric node coordinates,
        `\\boldsymbol{b}_{\\boldsymbol{x}}(\\alpha) \\in \\mathbb{R}^{\\#\\alpha}`
        has the base case

        .. math::
            :label: basecase

            \\boldsymbol{b}_{\\boldsymbol{x}}(\\alpha) = (x^{|\\alpha|}_{\\alpha_0}, x^{|\\alpha|}_{\\alpha_1}), \\quad \\#\\alpha = 2,

        and the recursion

        .. math::
            :label: recursion

            \\boldsymbol{b}_{\\boldsymbol{x}}(\\alpha) =
            \\frac{\\sum_i x^{|\\alpha|}_{|\\alpha_{\\backslash i}|} I^{\\#\\alpha}_i \\boldsymbol{b}_{\\boldsymbol{x}}(\\alpha_{\\backslash i})}
            {\\sum_i x^{|\\alpha|}_{|\\alpha_{\\backslash i}|}}, \\quad \\#\\alpha > 2.

        The full set of nodes is

        .. math:: \\boldsymbol{b}_{\\boldsymbol{x}}^{d,n} = \\{\\boldsymbol{b}_{\\boldsymbol{x}}(\\alpha): \\#\\alpha = d+1, |\\alpha| = n\\}.
            :label: fullset

    Args:
        d (int): The dimension of the simplex
        n (int): The maximum degree of the polynomials
        family (optional): The 1D node family used to define the coordinates in the barycentric `d`-simplex.
            The default ``family='lgl'`` corresponds to the shifted Lobatto-Gauss-Legendre_ nodes.
            See ":ref:`families`" for using other node families.
        domain (str, optional): The domain for the `d`-simplex where the returned coordinates will be defined.
            See ":ref:`domains`" for the choices and their formal definitions.

    Returns:
        ndarray: The nodes `\\boldsymbol{b}_{\\boldsymbol{x}}^{d,n}` defined in
        :eq:`fullset`, as a 2D array with `\\binom{n+d}{d}` rows.  If
        ``domain='barycentric'``, it has `d+1` columns, otherwise it has `d`
        columns.

    Examples:

        Nodes for `\\mathcal{P}^4(\\Delta^2)` in barycentric coordinates:

        >>> recursive_nodes(2, 4)
        array([[0.        , 0.        , 1.        ],
               [0.        , 0.17267316, 0.82732684],
               [0.        , 0.5       , 0.5       ],
               [0.        , 0.82732684, 0.17267316],
               [0.        , 1.        , 0.        ],
               [0.17267316, 0.        , 0.82732684],
               [0.2221552 , 0.2221552 , 0.5556896 ],
               [0.2221552 , 0.5556896 , 0.2221552 ],
               [0.17267316, 0.82732684, 0.        ],
               [0.5       , 0.        , 0.5       ],
               [0.5556896 , 0.2221552 , 0.2221552 ],
               [0.5       , 0.5       , 0.        ],
               [0.82732684, 0.        , 0.17267316],
               [0.82732684, 0.17267316, 0.        ],
               [1.        , 0.        , 0.        ]])

        The same nodes on the unit triangle:

        >>> recursive_nodes(2, 4, domain='unit')
        array([[0.        , 0.        ],
               [0.        , 0.17267316],
               [0.        , 0.5       ],
               [0.        , 0.82732684],
               [0.        , 1.        ],
               [0.17267316, 0.        ],
               [0.2221552 , 0.2221552 ],
               [0.2221552 , 0.5556896 ],
               [0.17267316, 0.82732684],
               [0.5       , 0.        ],
               [0.5556896 , 0.2221552 ],
               [0.5       , 0.5       ],
               [0.82732684, 0.        ],
               [0.82732684, 0.17267316],
               [1.        , 0.        ]])

        If we construct the node set not from the Lobatto-Gauss-Legendre 1D node family,
        but from the equispaced 1D node family, we get equispaced 2D nodes:

        >>> recursive_nodes(2, 4, family='equi', domain='unit')
        array([[0.  , 0.  ],
               [0.  , 0.25],
               [0.  , 0.5 ],
               [0.  , 0.75],
               [0.  , 1.  ],
               [0.25, 0.  ],
               [0.25, 0.25],
               [0.25, 0.5 ],
               [0.25, 0.75],
               [0.5 , 0.  ],
               [0.5 , 0.25],
               [0.5 , 0.5 ],
               [0.75, 0.  ],
               [0.75, 0.25],
               [1.  , 0.  ]])

        This is what they look like mapped to the equilateral triangle:

        .. plot::
           :include-source: True

           >>> import matplotlib.pyplot as plt
           >>> from recursivenodes import recursive_nodes
           >>> nodes_equi = recursive_nodes(2, 4, family='equi', domain='equilateral')
           >>> nodes_lgl = recursive_nodes(2, 4, domain='equilateral')
           >>> plt.scatter(nodes_lgl[:,0], nodes_lgl[:,1], marker='o', label='recursive LGL')
           <matplotlib.collections.PathCollection object at ...>
           >>> plt.scatter(nodes_equi[:,0], nodes_equi[:,1], marker='^', label='equispaced')
           <matplotlib.collections.PathCollection object at ...>
           >>> plt.gca().set_aspect('equal')
           >>> plt.legend()
           <matplotlib.legend.Legend object at ...>
           >>> plt.show()


    .. _multi-index: https://en.wikipedia.org/wiki/Multi-index_notation
    .. _barycentric triangle: https://en.wikipedia.org/wiki/Barycentric_coordinate_system
    .. _Lobatto-Gauss-Legendre: https://en.wikipedia.org/wiki/Gaussian_quadrature#Gauss%E2%80%93Lobatto_rules

    '''
    family = _decode_family(family)
    N = npolys(d, n)
    x = np.zeros((N, d+1))
    for (k, i) in enumerate(multiindex_equal(d+1, n)):
        x[k, :] = _recursive(d+1, n, i, family)
    return coord_map(x, 'barycentric', domain)


def expand_to_boundary(d, n, nodes, ex_nodes, domain='biunit'):
    ''' given degree n nodes for the d-simplex that are logically laid out like
    the equispaced nodes and are only in the interior, construct degree (n + d
    + 1) nodes for the d-simplex which are equal to nodes in the interior and
    ex_nodes on the boundary.  No attempt is made to make the new boundary
    nodes good for interpolation: they are just there to aid in computing
    lebesguemax() in lebesgue.py '''
    nd = n + d + 1
    tuple_to_index = {}
    for (k, i) in enumerate(multiindex_equal(d+1, n)):
        tuple_to_index[i] = k
    ex_nodes = ex_nodes.copy()
    for (k, i) in enumerate(multiindex_equal(d+1, nd)):
        if min(i) > 0:
            ihat = tuple([a - 1 for a in i])
            j = tuple_to_index[ihat]
            ex_nodes[k, :] = nodes[j, :]
    return ex_nodes


def add_nodes_to_parser(parser):
    parser.add_argument('-n', '--degree', type=int, nargs='?', default=7,
                        help='degree of polynomial space for which node set is equisolvent')
    parser.add_argument('-d', '--dimension', type=int, nargs='?', default=3,
                        help='spatial dimensions to node set simplex')
    parser.add_argument('--nodes', type=str,
                        choices=['recursive', 'warburton', 'blyth_luo_pozrikidis', 'equispaced', 'equispaced_interior'],
                        nargs='?', default='recursive',
                        help='node placement algorithm')
    parser.add_argument('-w', '--w-alpha', type=float, nargs='?',
                        help='blending parameter for Warburton warp & blend method')
    parser.add_argument('--domain', type=str,
                        choices=['biunit', 'unit', 'barycentric', 'equilateral'],
                        default='biunit', nargs='?',
                        help='output simlex domain')
    parser.add_argument('-f', '--family', type=str, choices=['lgl', 'lgc', 'gl', 'gc', 'equi', 'equi_interior', 'lgg', 'gg'],
                        default='lgl', nargs='?',
                        help='base 1D node family for Blyth-Pozrikidis, Warburton, and recursive nodes')
    parser.add_argument('-g', '--g-alpha', type=float, nargs='?', default=0.,
                        help='Gegenbauer alpha exponent (only used with --family lgg or --family gg)')


def nodes_from_args(args, expanded=False):
    d = args.dimension
    n = args.degree
    domain = args.domain
    fam_arg = args.family
    need_expanded = False
    if expanded:
        need_expanded = True
        if args.nodes == 'equispaced' or (args.nodes != 'equispaced_interior' and (args.family == 'equi' or fam_arg[0] == 'l')):
            need_expanded = False
    if need_expanded:
        if args.nodes == 'equispaced_interior' or args.family == 'equi_interior':
            ex_fam_arg = 'equi'
        else:
            ex_fam_arg = 'l' + fam_arg
    if (fam_arg == 'lgg' or fam_arg == 'gg'):
        fam_arg = (fam_arg, args.g_alpha)
    family = _decode_family(fam_arg)
    x = coord_map(family[n], 'unit', domain)
    if need_expanded:
        if (ex_fam_arg == 'lgg'):
            ex_fam_arg = (ex_fam_arg, args.g_alpha)
        ex_family = _decode_family(ex_fam_arg)
        ex_x = coord_map(family[n+d+1], 'unit', domain)
    if args.nodes == 'equispaced':
        nodes = equispaced(d, n, domain=domain)
    elif args.nodes == 'equispaced_interior':
        nodes = equispaced_interior(d, n, domain=domain)
        if need_expanded:
            ex_nodes = equispaced(d, n+d+1, domain=domain)
    elif args.nodes == 'blyth_luo_pozrikidis':
        nodes = blyth_luo_pozrikidis(d, n, x, domain=domain)
        if need_expanded:
            ex_nodes = blyth_luo_pozrikidis(d, n+d+1, ex_x, domain=domain)
    elif args.nodes == 'warburton':
        alpha = args.w_alpha
        nodes = warburton(d, n, x, alpha=alpha, domain=domain)
        if need_expanded:
            ex_nodes = warburton(d, n+d+1, ex_x, alpha=alpha, domain=domain)
    elif args.nodes == 'recursive':
        nodes = recursive(d, n, family, domain=domain)
        if need_expanded:
            ex_nodes = recursive(d, n+d+1, ex_family, domain=domain)
    if expanded:
        if need_expanded:
            ex_nodes = expand_to_boundary(d, n, nodes, ex_nodes, domain=domain)
            return (d, n, domain, family, nodes, ex_nodes)
        else:
            return (d, n, domain, family, nodes, nodes)
    return (d, n, domain, family, nodes)


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(description='Print out a node set implemented in nodes.py')
    add_nodes_to_parser(parser)
    args = parser.parse_args()
    d, n, domain, family, nodes = nodes_from_args(args)
    print(nodes)
