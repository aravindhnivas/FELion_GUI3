
import shutil, os, json
from os.path import join 
from pathlib import Path as pt


# DATA Analysis

from uncertainties import ufloat as uf, unumpy as unp
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d

from uncertainties import ufloat as uf, unumpy as unp

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

def convert_intesities(felixlocation, output_filename, wn, inten, norm_method):
    if pt(f"{felixlocation}/{output_filename}.felix").exists(): felixfile = felixlocation / f"{output_filename}.felix"
    else: felixfile = felixlocation / f"{output_filename}.cfelix"
    
    powerfile = felixlocation / f"{output_filename}.pow"
    with open(powerfile) as f:
        for line in f:
            if line[0] == "#":
                if line.find("Hz") > -1:
                    felix_hz = int(line.split(" ")[1])
                    break
    
    pow_x, pow_y = np.genfromtxt(powerfile).T
    intepd_power = interp1d(pow_x, pow_y, kind="linear",  fill_value='extrapolate')
    power_measured = intepd_power(wn)
    felix_hz = int(felix_hz)
    res, b0, trap = var_find(felixfile)

    nshots = int((trap/1000) * felix_hz)
    total_power = power_measured*nshots
    if norm_method == "Relative": ratio = -((inten/100)-1)
    elif norm_method == "Log": ratio = np.e**(-(inten/1000)*total_power)
    else:
        logInten = (inten*1e3)/wn
        ratio = np.e**(-(logInten/1000)*total_power)
    log_intensity = (-unp.log(ratio)/total_power)*1000

    log_hv_intensity = (wn * log_intensity) / 1e3
    relative_depletion =(1-ratio)*100
    return [relative_depletion.nominal_value, relative_depletion.std_dev],      [log_intensity.nominal_value, log_intensity.std_dev], [log_hv_intensity.nominal_value, log_hv_intensity.std_dev]