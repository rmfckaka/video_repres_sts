"""C3D"""
import math
from collections import OrderedDict

import torch
import torch.nn as nn
from torch.nn.modules.utils import _triple


class c3d_BN(nn.Module):
    """C3D with BN and pool5 to be AdaptiveAvgPool3d(1)."""

    def __init__(self, motion_dims=14, app_dims=13):
        super(c3d_BN, self).__init__()
        self.motion_dims = motion_dims
        self.app_dims = app_dims

        self.conv1 = nn.Conv3d(3, 64, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn1 = nn.BatchNorm3d(64)
        self.relu1 = nn.ReLU()
        self.pool1 = nn.MaxPool3d(kernel_size=(1, 2, 2), stride=(1, 2, 2))

        self.conv2 = nn.Conv3d(64, 128, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn2 = nn.BatchNorm3d(128)
        self.relu2 = nn.ReLU()
        self.pool2 = nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))

        self.conv3a = nn.Conv3d(128, 256, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn3a = nn.BatchNorm3d(256)
        self.relu3a = nn.ReLU()
        self.conv3b = nn.Conv3d(256, 256, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn3b = nn.BatchNorm3d(256)
        self.relu3b = nn.ReLU()
        self.pool3 = nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))

        self.conv4a = nn.Conv3d(256, 512, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn4a = nn.BatchNorm3d(512)
        self.relu4a = nn.ReLU()
        self.conv4b = nn.Conv3d(512, 512, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn4b = nn.BatchNorm3d(512)
        self.relu4b = nn.ReLU()
        self.pool4 = nn.MaxPool3d(kernel_size=(2, 2, 2), stride=(2, 2, 2))

        self.conv5a = nn.Conv3d(512, 512, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn5a = nn.BatchNorm3d(512)
        self.relu5a = nn.ReLU()
        self.conv5b = nn.Conv3d(512, 512, kernel_size=(3, 3, 3), padding=(1, 1, 1))
        self.bn5b = nn.BatchNorm3d(512)
        self.relu5b = nn.ReLU()

        self.pool5 = nn.AdaptiveAvgPool3d(1)
        self.motion_linear = nn.Linear(512, self.motion_dims)
        self.app_linear = nn.Linear(512, self.app_dims)

    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu1(x)
        x = self.pool1(x)

        x = self.conv2(x)
        x = self.bn2(x)
        x = self.relu2(x)
        x = self.pool2(x)

        x = self.conv3a(x)
        x = self.bn3a(x)
        x = self.relu3a(x)
        x = self.conv3b(x)
        x = self.bn3b(x)
        x = self.relu3b(x)
        x = self.pool3(x)

        x = self.conv4a(x)
        x = self.bn4a(x)
        x = self.relu4a(x)
        x = self.conv4b(x)
        x = self.bn4b(x)
        x = self.relu4b(x)
        x = self.pool4(x)

        x = self.conv5a(x)
        x = self.bn5a(x)
        x = self.relu5a(x)
        x = self.conv5b(x)
        x = self.bn5b(x)
        x = self.relu5b(x)

        x = self.pool5(x)
        x = x.view(-1, 512)

        motion_out = self.motion_linear(x)
        app_out = self.app_linear(x)

        return motion_out, app_out


def get_1x_lr_params(model):
    """
    This generator returns all the parameters of weights
    """

    for name, param in model.named_parameters():
        if 'weight' in name and param.requires_grad:
            # print (name, param.data)

            yield param



def get_2x_lr_params(model):
    """
    This generator returns all the parameters of bias
    """

    for name, param in model.named_parameters():
        if 'bias' in name and param.requires_grad:
            # print (name, param.data)

            yield param


if __name__ == '__main__':
    c3d = c3d_BN()
    input = torch.randn((2, 3, 16, 112, 112))
    motion_out, app_out = c3d(input)
    print(motion_out.shape, app_out.shape)