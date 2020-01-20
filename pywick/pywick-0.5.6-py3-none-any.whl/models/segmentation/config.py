import os

# here (https://github.com/pytorch/vision/tree/master/torchvision/models) to find the download link of pretrained models

root = '/models/pytorch'
res50_path = os.path.join(root, 'resnet50-19c8e357.pth')
res101_path = os.path.join(root, 'resnet101-5d3b4d8f.pth')
res152_path = os.path.join(root, 'resnet152-b121ed2d.pth')
inception_v3_path = os.path.join(root, 'inception_v3_google-1a9a5a14.pth')
vgg19_bn_path = os.path.join(root, 'vgg19_bn-c79401a0.pth')
vgg16_path = os.path.join(root, 'vgg16-397923af.pth')
dense201_path = os.path.join(root, 'densenet201-4c113574.pth')

'''
vgg16 trained using caffe
visit this (https://github.com/jcjohnson/pytorch-vgg) to download the converted vgg16
'''
vgg16_caffe_path = os.path.join(root, 'vgg16-caffe.pth')
