#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for MultiRank"""

import unittest

import numpy as np
from scipy import sparse

from sknetwork.soft_classification import MultiRank, BiMultiRank
from sknetwork.data import painters, movie_actor


# noinspection DuplicatedCode
class TestMultiRank(unittest.TestCase):

    def test_multirank(self):
        adjacency: sparse.csr_matrix = painters()
        adj_array_seeds = -np.ones(adjacency.shape[0])
        adj_array_seeds[:2] = np.arange(2)
        adj_dict_seeds = {0: 0, 1: 1}

        mr = MultiRank(solver='lsqr')
        membership1 = mr.fit_transform(adjacency, adj_array_seeds)
        membership2 = mr.fit_transform(adjacency, adj_dict_seeds)
        self.assertTrue(np.allclose(membership1, membership2))
        self.assertEqual(membership2.shape, (adjacency.shape[0], 2))

    def test_bimultirank(self):
        biadjacency: sparse.csr_matrix = movie_actor()
        biadj_array_seeds = -np.ones(biadjacency.shape[0])
        biadj_array_seeds[:2] = np.arange(2)
        biadj_array_seeds = biadj_array_seeds
        biadj_dict_seeds = {0: 0, 1: 1}

        bmr = BiMultiRank()
        bmr.fit(biadjacency, biadj_array_seeds)
        membership1 = bmr.membership_.copy()
        bmr.fit(biadjacency, biadj_dict_seeds)
        membership2 = bmr.membership_.copy()
        self.assertTrue(np.allclose(membership1, membership2))
        self.assertEqual(membership2.shape, (biadjacency.shape[0], 2))
