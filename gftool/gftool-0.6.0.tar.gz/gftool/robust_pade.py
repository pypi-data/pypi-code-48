"""Implementation of Padé based on robust pole finding."""
import numpy as np
import scipy.linalg as spla
import scipy.optimize as spopt
import scipy.odr

from numpy.polynomial import polynomial

import gftool as gt


def number_poles(z, fct_z, *, M_min_N=1, weight=False, M_start=50, vandermond=polynomial.polyvander):
    """Estimate the optimal number of poles for a rational approximation.

    Parameters
    ----------
    z, fct_z : (N_z) complex np.ndarray
        Variable where function is evaluated and function values.
    M_min_N : int, optional
        The difference of denominator and nominator degree. (default: 1)
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.
    M_start : int, optional
        Starting guess for the number of poles. Can be given to speed up
        calculation if a good estimate is available.
    vandermond : Callable, optional
        Function giving the Vandermond matrix of the chosen polynomial basis.

    Returns
    -------
    number_poles : int
        Best guess for optimal number of poles.

    """
    tol = np.finfo(fct_z.dtype).eps
    max_n_poles = abs_max_n_poles = (z.size + M_min_N)//2
    n_poles = M_start
    n_roots = n_poles - M_min_N
    assert n_poles <= max_n_poles
    assert n_poles + n_roots < z.size
    while True:
        n_roots = n_poles - M_min_N
        vander = vandermond(z, deg=max(n_poles, n_roots)+1)
        fct_denom = fct_z[:, np.newaxis]*vander[..., :n_poles+1]
        nomin = vander[..., :n_roots+1]
        # TODO: check if [fct_denom, nomin] is the better choice
        scaling = 1./np.linalg.norm(nomin, axis=-1, keepdims=True)
        # FIXME
        scaling = 1./np.linalg.norm(np.concatenate((vander[..., :n_poles+1], nomin), axis=-1), axis=-1, keepdims=True)
        if np.any(weight):
            scaling *= weight[..., np.newaxis]
        q_fct_x_denom, __ = np.linalg.qr(scaling*fct_denom)
        q_nomin, __ = np.linalg.qr(scaling*nomin)
        mat = np.concatenate([q_fct_x_denom, q_nomin], axis=-1)
        singular_values = np.linalg.svd(mat, compute_uv=False)
        null_dim = np.count_nonzero(singular_values < tol*singular_values[0]*max(mat.shape))
        if null_dim == 1:  # correct number of poles
            import matplotlib.pyplot as plt

            plt.plot(singular_values, 'x--')
            plt.yscale('log')
            plt.show()
            return n_poles
        if null_dim == 0:  # too few poles
            if n_poles == abs_max_n_poles:
                raise RuntimeError(
                    f"No solution with {abs_max_n_poles} poles or less could be found!"
                )
            if n_poles == max_n_poles:
                print("Warning: residue is bigger then tolerance: "
                      f"{singular_values[-1]/singular_values[0]}.")
                return n_poles
            # increase number of poles
            n_poles = min(2*n_poles, max_n_poles)
        else:  # already too many poles
            max_n_poles = n_poles - 1
            n_poles = n_poles - (null_dim + M_min_N)//2


def poles(z, fct_z, *, N: int = None, M: int, vandermond=polynomial.polyvander, weight=False):
    """Calculate position of `M` poles.

    Parameters
    ----------
    z, fct_z : (N_z) complex np.ndarray
        Variable where function is evaluated and function values.
    N, M : int
        Number of roots and poles of the function.
        For large `z` the function is proportional to `z**(N - M)`.
        (`N` defaults to `M-1`)
    vandermond : Callable, optional
        Function giving the Vandermond matrix of the chosen polynomial basis.
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.

    Returns
    -------
    poles : (M) complex np.ndarray
        The position of the poles.

    """
    if N is None:
        N = M - 1
    fct_z = fct_z/np.median(fct_z)
    vander = vandermond(z, deg=max(N+1, M))
    nomin = -vander[..., :N+1]
    fct_denom = fct_z[..., np.newaxis]*vander[..., :M]
    scaling = 1./np.linalg.norm(fct_denom, axis=-1, keepdims=True)
    # FIXME
    scaling = 1./np.linalg.norm(np.concatenate((vander[..., :M], nomin), axis=-1), axis=-1, keepdims=True)
    if np.any(weight):
        scaling *= weight[..., np.newaxis]
    q_nomin, __ = np.linalg.qr(scaling*nomin, mode='complete')
    q_fct_denom, __ = np.linalg.qr(scaling*fct_denom, mode='reduced')
    # q_fct_denom, *__ = spla.qr(D*B1, mode='economic', pivoting=True)
    qtilde_z_fct_denom = q_nomin[..., N+1:].T.conj() @ (z[..., np.newaxis] * q_fct_denom)
    qtilde_fct_denom = q_nomin[..., N+1:].T.conj() @ q_fct_denom
    __, __, vh = np.linalg.svd(np.concatenate((qtilde_z_fct_denom, qtilde_fct_denom), axis=-1))
    return spla.eig(vh[:M, :M], vh[:M, M:], right=False)


def roots(z, fct_z, poles, *, N: int = None, vandermond=polynomial.polyvander, weight=False):
    """Calculate position of `N` roots given the `poles`.

    Parameters
    ----------
    z, fct_z : (N_z) complex np.ndarray
        Variable where function is evaluated and function values.
    poles : (M) complex np.ndarray
        Position of the poles of the function
    N : int
        Number of roots.
        For large `z` the function is proportional to `z**(N - M)`.
        (`N` defaults to `M-1`)
    vandermond : Callable, optional
        Function giving the Vandermond matrix of the chosen polynomial basis.
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.

    Returns
    -------
    roots : (N) complex np.ndarray
        The position of the roots.

    """
    M = poles.size
    if N is None:
        N = M - 1
    denom = np.prod(np.subtract.outer(z, poles), axis=-1)
    fct_denom = (fct_z*denom)[:, np.newaxis]
    nomin = vandermond(z, deg=N-1)
    scaling = 1./np.linalg.norm(fct_denom, axis=-1, keepdims=True)
    # FIXME
    scaling = 1./np.linalg.norm(np.concatenate((denom[..., np.newaxis], nomin), axis=-1), axis=-1, keepdims=True)
    # scaling = 1./np.linalg.norm(nomin, axis=-1, keepdims=True)
    if np.any(weight):
        scaling *= weight[..., np.newaxis]
    q_fct_denom, __ = np.linalg.qr(scaling*fct_denom, mode='complete')
    q_nomin, __ = np.linalg.qr(scaling*nomin, mode='reduced')
    qtilde_z_nomin = q_fct_denom[:, 1:].T.conj() @ (z[..., np.newaxis] * q_nomin)
    qtilde_nomin = q_fct_denom[:, 1:].T.conj() @ q_nomin
    __, __, vh = np.linalg.svd(np.concatenate((qtilde_z_nomin, qtilde_nomin), axis=-1))
    return spla.eig(vh[:N, :N], vh[:N, N:], right=False)


def residues_ols(z, fct_z, poles, weight=False):
    """Calculate the residues using ordinary least square.

    Parameters
    ----------
    z, fct_z : (N_z) complex np.ndarray
        Variable where function is evaluated and function values.
    poles : (M) complex np.ndarray
        Position of the poles of the function
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.

    Returns
    -------
    residues : (M) complex np.ndarray
        The residues corresponding to the `poles`.

    """
    polematrix = 1./np.subtract.outer(z, poles)
    if np.any(weight):
        polematrix *= weight[..., np.newaxis]
        fct_z = fct_z*weight
    return np.linalg.lstsq(polematrix, fct_z, rcond=None)[:2]


def residues_ols_tau_b(tau, fct_tau, poles, beta, weight=False):
    """Calculate the residues using ordinary least square.

    Parameters
    ----------
    z, fct_z : (N_z) complex np.ndarray
        Variable where function is evaluated and function values.
    poles : (M) complex np.ndarray
        Position of the poles of the function
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.

    Returns
    -------
    residues : (M) complex np.ndarray
        The residues corresponding to the `poles`.

    """
    polematrix_tau = gt.pole_gf_tau(tau, weights=1, poles=poles[:, np.newaxis], beta=beta)
    assert polematrix_tau.shape == tau.shape + poles.shape
    # polematrix = 1./np.subtract.outer(z, poles)
    if np.any(weight):
        # polematrix *= weight[..., np.newaxis]
        polematrix_tau *= weight[..., np.newaxis]
        fct_tau = fct_tau*weight
    return np.linalg.lstsq(polematrix_tau, fct_tau, rcond=None)[:2]


def residues_tls(z, fct_z, poles, weight=None, constrains=None):
    polematrix = 1./np.subtract.outer(z, poles)
    if weight is not None:
        polematrix *= weight[..., np.newaxis]
        fct_z *= weight
    if constrains is not None:
        # TODO: add constrains
        raise NotImplementedError
    __, sigma, vh = np.linalg.svd(np.concatenate((polematrix, fct_z[..., np.newaxis]), axis=-1))
    print('TLS sigma: ', sigma)
    print(vh.shape, vh[-1, -1])
    return -vh[-1, :-1]/vh[-1, -1]


def residues_odr(z, fct_z, poles, weight=False):
    """Calculate the residues using orthogonal distance regression.

    This assumes that not only `fct_z` contains errors, but also `poles`.

    Parameters
    ----------
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.

    Returns
    -------
    residues : (M) complex np.ndarray
        The residues corresponding to the `poles`.

    """
    def odr_residues(residues_, pole_matrix):
        import ipdb; ipdb.set_trace()
        return np.sum(pole_matrix.T*residues_, axis=-1)[np.newaxis]
        return gt.pole_gf_z(z, poles=poles_, weights=residues_)

    regression = scipy.odr.ODR(
        data=scipy.odr.Data(x=1./(z - poles[:, np.newaxis]), y=fct_z[np.newaxis]),
        model=scipy.odr.Model(odr_residues),
        beta0=residues_ols(z, fct_z, poles=poles, weight=weight)[0],
    ).run()

    return regression


def asymtotic(z, fct_z, roots, poles, weight=False):
    """Calculate large `z` asymptotic from `roots` and `poles`.

    Parameters
    ----------
    z, fct_z : (N_z) complex np.ndarray
        Variable where function is evaluated and function values.
    poles : (M) complex np.ndarray
        Position of the poles of the function.
    roots : (N) complex np.ndarray
        Position of the roots of the function.
    weight : (N_z) float np.ndarray, optional
        Weighting of the data points, for a known error `σ` this should be
        `weight = 1./σ`.

    Returns
    -------
    asym, std : float
        Large `z` asymptotic and its standard deviation.

    """
    ratios = fct_z/np.prod(np.subtract.outer(z, roots), axis=-1) \
        * np.prod(np.subtract.outer(z, poles), axis=-1)
    if weight is False:
        asym = np.mean(ratios, axis=-1)
        std = np.std(ratios, ddof=1, axis=-1)
    else:
        asym = np.average(ratios, weights=weight, axis=-1)
        std = np.average(abs(ratios - asym)**2, weights=weight, axis=-1)
    return asym, std


def physical(z, fct_z, poles0, weights0, weight):
    num = 10000  # mesh points on which positivity is checked
    # starting from a good guess, fit the poles

    def pole_gf(z_, *params):
        z_ = z_.view(complex)
        params = np.array(params).view(complex)
        weights = params[:weights0.size]
        poles = params[weights0.size:]
        # check for 10 halfwidths
        lower = min(poles0.real + 10*abs(poles.imag))
        upper = max(poles0.real + 10*abs(poles.imag))
        relevant = np.linspace(lower, upper, num=num)
        check = gt.pole_gf_z(relevant, poles, weights=weights).imag
        check[check < 0] = 0
        return np.concatenate((gt.pole_gf_z(z_, poles, weights=weights).view(float), check))

    # import ipdb; ipdb.set_trace()
    pole_bounds_upper = np.empty_like(poles0)
    pole_bounds_upper.real = np.infty
    pole_bounds_upper.imag = 0
    pole_bounds_lower = np.empty_like(poles0)
    pole_bounds_lower.real = -np.infty
    pole_bounds_lower.imag = -np.infty
    weight_bounds_upper = np.empty_like(weights0)
    weight_bounds_upper.real = np.infty
    weight_bounds_upper.imag = np.infty
    weight_bounds_lower = np.empty_like(weights0)
    weight_bounds_lower.real = -np.infty
    weight_bounds_lower.imag = -np.infty

    # if weights0[np.argmax(poles0.real)] < 0:
    #     print('WARNING rightmost pole has negative residue!!')
    # else:
    #     weight_bounds_lower[np.argmax(weights0.real)] = 0
    # if weights0[np.argmin(poles0.real)] < 0:
    #     print('WARNING leftmost pole has negative residue!!')
    # else:
    #     weight_bounds_lower[np.argmin(weights0.real)] = 0

    if weight is not None:
        sigma = 1./(weight if np.iscomplexobj(weight) else weight + 1j*weight).view(float)
        sigma = np.concatenate((sigma, np.full(num, sigma.min())))
    else:
        sigma = None

    weights0[weights0 < 0] = 0

    fit, __ = spopt.curve_fit(
        pole_gf, xdata=z.view(float), ydata=np.concatenate((fct_z.view(float), np.zeros(num))),
        p0=np.concatenate((weights0.view(float), poles0.view(float))),
        bounds=(np.concatenate((weight_bounds_lower.view(float), pole_bounds_lower.view(float))),
                np.concatenate((weight_bounds_upper.view(float), pole_bounds_upper.view(float)))),
        sigma=sigma,
    )
    fit = np.array(fit).view(complex)
    weights = fit[:weights0.size]
    poles = fit[weights0.size:]
    initial_residue = abs(fct_z - pole_gf(z, *weights0.view(float), *poles0.view(float)).view(complex)[:fct_z.size])
    final_residue = abs(fct_z - pole_gf(z, *weights.view(float), *poles.view(float)).view(complex)[:fct_z.size])
    print('init ', initial_residue)
    print('final', final_residue)
    return poles, weights


def physical_strict(z, fct_z, poles0, weights0, weight):
    # starting from a good guess, fit the poles
    def pole_gf(z_, *params):
        z_ = z_.view(complex)
        weights = np.array(params[:weights0.size])
        poles = np.array(params[weights0.size:]).view(complex)
        return gt.pole_gf_z(z_, poles, weights=weights).view(float)

    # import ipdb; ipdb.set_trace()
    pole_bounds_upper = np.empty_like(poles0)
    pole_bounds_upper.real = np.infty
    pole_bounds_upper.imag = 0
    pole_bounds_lower = np.empty_like(poles0)
    pole_bounds_lower.real = -np.infty
    pole_bounds_lower.imag = -np.infty
    weigt_bounds_upper = np.full_like(weights0.real, +np.infty)
    weigt_bounds_lower = np.full_like(weights0.real, 0)

    if weight is not None:
        sigma = 1./(weight if np.iscomplexobj(weight) else weight + 1j*weight).view(float)
    else:
        sigma = None

    weights0[weights0 < 0] = 0

    fit, __ = spopt.curve_fit(
        pole_gf, xdata=z.view(float), ydata=fct_z.view(float),
        p0=np.concatenate((weights0.real, poles0.view(float))),
        bounds=(np.concatenate((weigt_bounds_lower, pole_bounds_lower.view(float))),
                np.concatenate((weigt_bounds_upper, pole_bounds_upper.view(float)))),
        sigma=sigma,
    )
    weights = fit[:weights0.size]
    poles = fit[weights.size:].view(complex)
    initial_residue = abs(fct_z - pole_gf(z, *weights0.real, *poles0.view(float)).view(complex))
    final_residue = abs(fct_z - pole_gf(z, *weights.real, *poles.view(float)).view(complex))
    print('init ', initial_residue)
    print('final', final_residue)
    return poles, weights
