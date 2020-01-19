#################################################################

# Modules
import shutil, os, json
from os.path import join 
from pathlib import Path as pt

# DATA Analysis
from lmfit.models import GaussianModel
from uncertainties import ufloat as uf
import numpy as np


def move(pathdir, x): return (shutil.move(join(pathdir, x), join(pathdir, "DATA", x)), print("%s moved to DATA folder" % x))

class gauss_fit:

    def __init__(self, x, y):

        # Gaussian model with guessing init. values
        model = GaussianModel()
        guess = model.guess(y, x=x)
        guess_values = guess.valuesdict()

        # Fitting gaussian curve with guessed values
        fit = model.fit(y, x=x, amplitude = guess_values['amplitude'], center = guess_values['center'],  sigma = guess_values['sigma'])

        # Fitted datas: Line freq, sigma and A
        fit_data = fit.best_fit
        line_freq_fit = fit.best_values['center']
        sigma = fit.best_values['sigma']
        A = fit.best_values['amplitude']

        # FWHM and Amplitude from fitted sigma
        fwhm = 2*sigma*np.sqrt(2*np.log(2))
        amplitude = A/(sigma*np.sqrt(2*np.pi))
        
        # Gettign error value for sig, freq and A from fit
        covar_matrix = fit.covar
        varience = np.diag(covar_matrix)
        perr = np.sqrt(varience)

        sigma_err, line_freq_err, A_err = perr

        # Making uncertainties float for sig., A and freq
        usigma = uf(sigma, sigma_err)
        uA = uf(A, A_err)
        uline_freq = uf(line_freq_fit, line_freq_err)

        # Calculating FWHM and Amplitude
        ufwhm = 2*usigma*np.sqrt(2*np.log(2))
        uamplitude = uA/(usigma*np.sqrt(2*np.pi))

        # Deriving error from calculated FWHM and Amplitude

        amplitude_err = uamplitude.std_dev
        fwhm_err = ufwhm.std_dev

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