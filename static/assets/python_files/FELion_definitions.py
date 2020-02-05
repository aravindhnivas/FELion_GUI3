
import shutil, os, json
from os.path import join 
from pathlib import Path as pt


# DATA Analysis

from uncertainties import ufloat as uf, unumpy as unp
import numpy as np
from scipy.optimize import curve_fit


def gaussian(x, amp, sig, cen): return amp*np.exp(-0.5*((x-cen)/sig)**2)

def move(pathdir, x): return (shutil.move(join(pathdir, x), join(pathdir, "DATA", x)), print("%s moved to DATA folder" % x))

class gauss_fit:

    def __init__(self, x, y):
        print(f"Sigma Guessed: {(x[np.argmax(y)] - x.min())/4}")
        pop, pcov = curve_fit(gaussian, x, y, p0=[y.max(), (x[np.argmax(y)] - x.min())/4, x[np.argmax(y)] ])
        perr = np.sqrt(np.diag(pcov))
        uamplitude, usigma, uline_freq, = unp.uarray(pop, perr)
        fit_data = gaussian(x, *pop)
        ufwhm = 2*usigma*np.sqrt(2*np.log(2))
        self.fit_data, self.uline_freq, self.usigma, self.uamplitude, self.ufwhm = fit_data, uline_freq, usigma, uamplitude, ufwhm

    def get_data(self): return self.fit_data, self.uline_freq, self.usigma, self.uamplitude, self.ufwhm
    def get_std(self, value): return value.std_dev
    def get_value(self, value): return value.nominal_value

def var_find(filename, var=None, get_defaults=True):

    if var is None:
        var = {
            'res': 'm03_ao13_reso', 
            'b0': 'm03_ao09_width',
            'trap': 'm04_ao04_sa_delay'
        }

    with open(filename, 'r') as mfile:
        mfile = np.array(mfile.readlines())

    for line in mfile:
        if not len(line.strip()) == 0 and line.split()[0] == '#':
            for j in var:
                if var[j] in line.split():
                    var[j] = float(line.split()[-3])
    
    if get_defaults:
        res, b0, trap = round(var['res'], 2), int(var['b0']/1000), int(var['trap']/1000)
        return res, b0, trap

    else: return var

def read_dat_file(filename, norm_method):


    read_data = np.genfromtxt(filename).T
    xs = read_data[0]

    if norm_method == "Log": ys = read_data[1]
    elif norm_method == "Relative": ys = read_data[2]
    else: ys = read_data[3]
    return xs, ys

def sendData(dataToSend):

    with open(pt(__file__).parent / "data.json", 'w+') as f:
        data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(data)