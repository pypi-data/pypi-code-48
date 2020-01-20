#!/usr/bin/env python3
# coding: utf-8
"""
Created on July 10 2019

Authors:
Nathan De Lara <nathan.delara@telecom-paris.fr>
"""


def auto_solver(nnz: int, threshold: int = 1e4) -> str:
    """Recommend a solver for SVD or Eigenvalue decomposition depending of the size of the input matrix.
    Halko's randomized method is returned for big matrices and Lanczos for small ones.

    Parameters
    ----------
    nnz: int
        Number of non-zero entries of the matrix to decompose.
    threshold: int
        Threshold beyond which randomized methods are applied.

    Returns
    -------
    solver name: str
        'halko' or ' lanczos'

    """
    if nnz > threshold:
        return 'halko'
    else:
        return 'lanczos'
