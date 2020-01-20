#!/usr/bin/env python
# coding: utf-8
#
# Author:   Kazuto Nakashima
# URL:      http://kazuto1011.github.io
# Created:  2017-11-19

# Source: https://github.com/kazuto1011/deeplab-pytorch/tree/master/libs/models

"""
DeepLab v2 - `DeepLab: Semantic Image Segmentation with Deep Convolutional Nets, Atrous Convolution, and Fully Connected CRFs <https://arxiv.org/abs/1606.00915>`_.
"""

from collections import OrderedDict

import torch
import torch.nn as nn
import torch.nn.functional as F

from .resnet import _ConvBatchNormReLU, _ResBlock
from .msc import MSC


def DeepLabV2_ResNet101_MSC(n_classes):
    return MSC(
        scale=DeepLabV2(
            num_classes=n_classes, n_blocks=[3, 4, 23, 3], pyramids=[6, 12, 18, 24]
        ),
        pyramids=[0.5, 0.75],
)

class _ASPPModule(nn.Module):
    """Atrous Spatial Pyramid Pooling"""

    def __init__(self, in_channels, out_channels, pyramids):
        super(_ASPPModule, self).__init__()
        self.stages = nn.Module()
        for i, (dilation, padding) in enumerate(zip(pyramids, pyramids)):
            self.stages.add_module(
                "c{}".format(i),
                nn.Conv2d(
                    in_channels=in_channels,
                    out_channels=out_channels,
                    kernel_size=3,
                    stride=1,
                    padding=padding,
                    dilation=dilation,
                    bias=True,
                ),
            )

        for m in self.stages.children():
            nn.init.normal_(m.weight, mean=0, std=0.01)
            nn.init.constant_(m.bias, 0)

    def forward(self, x):
        h = 0
        for stage in self.stages.children():
            h += stage(x)
        return h


class DeepLabV2(nn.Sequential):

    def __init__(self, num_classes, n_blocks, pyramids, **kwargs):
        super(DeepLabV2, self).__init__()
        self.add_module(
            "layer1",
            nn.Sequential(
                OrderedDict(
                    [
                        ("conv1", _ConvBatchNormReLU(3, 64, 7, 2, 3, 1)),
                        ("pool", nn.MaxPool2d(3, 2, 1, ceil_mode=True)),
                    ]
                )
            ),
        )
        self.add_module("layer2", _ResBlock(n_blocks[0], 64, 64, 256, 1, 1))
        self.add_module("layer3", _ResBlock(n_blocks[1], 256, 128, 512, 2, 1))
        self.add_module("layer4", _ResBlock(n_blocks[2], 512, 256, 1024, 1, 2))
        self.add_module("layer5", _ResBlock(n_blocks[3], 1024, 512, 2048, 1, 4))
        self.add_module("aspp", _ASPPModule(2048, num_classes, pyramids))

    def forward(self, x):
        # return super(DeepLabV2, self).forward(x)
        logits = super(DeepLabV2, self).forward(x)
        logits = F.interpolate(logits, size=x.shape[2:], mode="bilinear", align_corners=True)
        return logits

    def freeze_bn(self):
        for m in self.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()


if __name__ == "__main__":
    model = DeepLabV2(num_classes=21, n_blocks=[3, 4, 23, 3], pyramids=[6, 12, 18, 24])
    model.freeze_bn()
    model.eval()
    print(list(model.named_children()))
    image = torch.randn(1, 3, 513, 513)
    print(model(image)[0].size())
