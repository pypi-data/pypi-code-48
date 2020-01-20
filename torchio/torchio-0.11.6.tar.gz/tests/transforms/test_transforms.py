#!/usr/bin/env python

import unittest
import torch
import numpy as np
from torchio import INTENSITY, LABEL, ImagesDataset

from torchio.transforms import (
    RandomFlip,
    RandomNoise,
    RandomBiasField,
    RandomElasticDeformation,
    RandomAffine,
    RandomMotion,
    Rescale,
    Resample,
    ZNormalization,
    HistogramStandardization,
    Pad,
    Crop,
)


class TestTransforms(unittest.TestCase):
    """Tests for all transforms."""

    def get_sample(self):
        shape = 1, 10, 20, 30
        np.random.seed(42)
        affine = np.diag((1, 2, 3, 1))
        affine[:3, 3] = 40, 50, 60
        sample = {
            't1': dict(
                data=self.getRandomData(shape),
                affine=affine,
                type=INTENSITY,
                stem='t1',
            ),
            't2': dict(
                data=self.getRandomData(shape),
                affine=affine,
                type=INTENSITY,
                stem='t2',
            ),
            'label': dict(
                data=(self.getRandomData(shape) > 0.5).float(),
                affine=affine,
                type=LABEL,
                stem='label',
            ),
        }
        return sample

    @staticmethod
    def getRandomData(shape):
        return torch.rand(*shape)

    def test_transforms(self):
        landmarks_dict = dict(
            t1=np.linspace(0, 100, 13),
            t2=np.linspace(0, 100, 13),
        )
        transforms = (
            Resample((1, 1.1, 1.25)),
            RandomFlip(axes=(0, 1, 2), flip_probability=1),
            RandomMotion(proportion_to_augment=1),
            RandomNoise(),
            RandomBiasField(),
            Rescale((0, 1)),
            ZNormalization(masking_method='label'),
            HistogramStandardization(landmarks_dict=landmarks_dict),
            RandomElasticDeformation(proportion_to_augment=1),
            RandomAffine(),
            Pad((1, 2, 3, 0, 5, 6)),
            Crop((3, 2, 8, 0, 1, 4)),
        )
        transformed = self.get_sample()
        for transform in transforms:
            transformed = transform(transformed)
