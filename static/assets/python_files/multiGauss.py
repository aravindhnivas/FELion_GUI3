# Importing Modules
from pathlib import Path as pt
import sys, json

# Data analysis
import numpy as np
from scipy.optimize import curve_fit

from uncertainties import ufloat as uf

# FELion module
from FELion_constants import colors

from FELion_definitions import sendData, read_dat_file
from scipy.interpolate import interp1d
from normline import var_find

def generateNGaussian(N):

    gaussfn = lambda n: f"A{n}*(np.exp((-1.0/2.0)*(((x-cen{n})/sigma{n})**2)))+"
    _gfn, _args = "", "x, "
    for i in range(int(N)): 
        _gfn += gaussfn(i)
        _args += f"cen{i}, A{i}, sigma{i}, "
    exec(f"gfn_ = lambda {_args.strip()[:-1]}: {_gfn.strip()[:-1]}")
    
    return locals()["gfn_"]

def filterWn(readfile, norm_method, index):
    wn, inten = read_dat_file(readfile, norm_method)
    print(f"Read data:\nwn: {wn.min():.2f} - {wn.max():.2f}\n")
    if not index: return wn, inten
    start_wn, end_wn = index
    
    print(f"Selecting data from {start_wn:.2f} - {end_wn:.2f}\n")
    index = np.logical_and(wn > start_wn, wn < end_wn)
    wn = wn[index]
    inten = inten[index]

    print(f"Processed data:\nwn: {wn.min():.2f} - {wn.max():.2f}\n")
    return wn, inten

def getColorIndex(fullfiles, output_filename):

    if output_filename == "averaged": line_color = "black"
    else:
        index = fullfiles.index(output_filename)
        index = 2*index
        if index > len(colors): 
            index = (index - len(colors)) - 1
            line_color = f"rgb{colors[index]}"
        else: line_color = f"rgb{colors[index]}"

    return line_color

def fitNGauss(init_guess, wn, inten):
    N = int(len(init_guess)/3)

    print(f"NGaussian: {N}\nInitialGuess: {init_guess}\n\n")
    gfn = generateNGaussian(N)
    popt_Ngauss, pcov_Ngauss = curve_fit(gfn, wn, inten, p0=init_guess)
    
    perr_Ngauss = np.sqrt(np.diag(pcov_Ngauss))
    popt_Ngauss_ = popt_Ngauss.reshape(N, 3)

    perr_Ngauss_ = perr_Ngauss.reshape(N, 3)

    print(f"\nFitted Parameters: {popt_Ngauss_}\nCovarience: {perr_Ngauss_}\n")
    return popt_Ngauss, popt_Ngauss_, perr_Ngauss_, gfn, N
    
def fitNGaussian(gauss_args):

    readfile = pt(gauss_args["peakFilename"])
    norm_method = gauss_args["normMethod"]
    output_filename = gauss_args["output_name"]
    fullfiles = [pt(i).stem for i in gauss_args["fullfiles"]]

    index = False
    if "index" in gauss_args: index = gauss_args["index"]
    wn, inten = filterWn(readfile, norm_method, index)
    line_color = getColorIndex(fullfiles, output_filename)

    fit_guesses = gauss_args["fitNGauss_arguments"]
    
    wn_found_peaks = [fit_guesses[key] for key in fit_guesses.keys() if key.startswith("cen")]
    filtered_index = np.in1d(wn, wn_found_peaks)

    init_guess = list(fit_guesses.values())
    popt_Ngauss, popt_Ngauss_, perr_Ngauss_, gfn, N = fitNGauss(init_guess, wn, inten)

    _sig = "\u03C3"
    _del = "\u0394"

    fwhm = lambda usigma: 2*usigma*np.sqrt(2*np.log(2))
    dataTosend = {}

    dataTosend["fitted_data"] = { "x":list(wn), "y":list(gfn(wn, *popt_Ngauss)),  "mode": "lines", "name":f"{N} Gaussian", "line": {"color":line_color} }
    dataTosend["fitted_parameter"] = [
        { "freq": f"{uf(fit[0], err[0]):.2uP}", "amp":f"{uf(fit[1], err[1]):.2uP}", "sig":f"{uf(fit[2], err[2]):.2uP}", "fwhm":f"{fwhm(uf(fit[2], err[2])):.2uP}"}
        for fit, err in zip(popt_Ngauss_, perr_Ngauss_)
    ]

    dataTosend["for_weighted_error"] = [
        f"{fit[0]}, {err[0]}, {fit[1]}, {err[1]}, {fwhm(uf(fit[2], err[2])).nominal_value}, {fwhm(uf(fit[2], err[2])).std_dev}, {fit[2]}, {err[2]}"
        for fit, err in zip(popt_Ngauss_, perr_Ngauss_)
    ]

    sendData(dataTosend)
    datfile = readfile.parent/f"{output_filename}.dat"
    overwrite = gauss_args["overwrite_expfit"]
    _data = np.genfromtxt(datfile)
    normMethods = ["Relative", "Log", "IntensityPerPhoton"]

    for method in normMethods:
        print(f"Fitting for method: {method}\n")
       
        _wn, _inten = filterWn(datfile, method, index)
       
        _guess_inten = _inten[filtered_index]
        print(f"Guessed Intesity: {_guess_inten}\n")

        for i, guess_amp in enumerate(_guess_inten): fit_guesses[f"A{i}"] = guess_amp
        
        init_guess = list(fit_guesses.values())
        try: _popt_Ngauss, _popt_Ngauss_, _perr_Ngauss_, _gfn, _N = fitNGauss(init_guess, _wn, _inten)
        except Exception as error: 
            raise Exception(f"Error while fitting {error}")        
            return

            
        _fitted_freq = np.array([_popt_Ngauss_, _perr_Ngauss_]).T[0]
        _fitted_inten = np.array([_popt_Ngauss_, _perr_Ngauss_]).T[1]
        _fitted_sigma = np.array([_popt_Ngauss_, _perr_Ngauss_]).T[2]

        expfile = readfile.parent/f"{output_filename}_{method}.expfit"
        fitfile = readfile.parent/f"{output_filename}_{method}.fullFit"
        
        with open(fitfile, ("a+", "w+")[overwrite]) as f:
        
            if overwrite: f.write(f"#Wn(cm-1)\tIntensity\n")
            for freq, inten in zip(_wn, gfn(_wn, *_popt_Ngauss)): f.write(f"{freq:.4f}\t{inten:.4f}\n")
    
        with open(expfile, ("a+", "w+")[overwrite]) as f:
            if overwrite: 
                f.write(f"#Frequency\tFreq_err\t#Intensity({method})\t#Intensity_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\n")
            fitted = np.array([_fitted_freq, _fitted_inten, _fitted_sigma])
            print(fitted, fitted.shape)
            for freq, amp, sigma in zip(*fitted):
                _fwhm = fwhm(uf(sigma[0], sigma[1]))
                _fwhm = [_fwhm.nominal_value, _fwhm.std_dev]
                if _fwhm[0] > 50: continue
                f.write(f"{freq[0]:.4f}\t{freq[1]:.4f}\t{amp[0]:.4f}\t{amp[1]:.4f}\t{sigma[0]:.4f}\t{sigma[1]:.4f}\t{_fwhm[0]:.4f}\t{_fwhm[1]:.4f}\n")

if __name__ == "__main__":
    
    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")

    fitNGaussian(args)