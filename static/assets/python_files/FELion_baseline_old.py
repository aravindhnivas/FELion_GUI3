import numpy as np
from scipy.interpolate import interp1d
import os
from tkinter.messagebox import showerror

def ReadBase(basefile):
    data = np.genfromtxt(f'./DATA/{basefile}')

    xs, ys = data[:,0], data[:,1]
    with open(f'./DATA/{basefile}', 'r') as f:
        interpol = f.readlines()[1].strip().split('=')[-1]
    return xs, ys, interpol

# Class for Baseline Calibration
class BaselineCalibrator(object):
    def __init__(self, basefile, ms=None):

        self.ms = ms
        self.Bx, self.By, self.interpol = ReadBase(basefile)
        self.f = interp1d(self.Bx, self.By, kind=self.interpol)

    def val(self, x):
        return self.f(x)
        
def felix_read_file(felixfile):

    file = np.genfromtxt(f'./DATA/{felixfile}')
    if felixfile.endswith('.felix'): data = file[:,0], file[:,2], file[:, 3]
    elif felixfile.endswith('.cfelix'): data = file[:,0], file[:,1], file[:, 2]
    return np.take(data, data[0].argsort(), 1)