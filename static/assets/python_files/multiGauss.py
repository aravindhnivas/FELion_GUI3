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

def generateNGaussian(N):

    gaussfn = lambda n: f"A{n}*(np.exp((-1.0/2.0)*(((x-cen{n})/sigma{n})**2)))+"
    _gfn, _args = "", "x, "
    for i in range(int(N)): 
        _gfn += gaussfn(i)
        _args += f"cen{i}, A{i}, sigma{i}, "
    exec(f"gfn_ = lambda {_args.strip()[:-1]}: {_gfn.strip()[:-1]}")
    
    return locals()["gfn_"]

def fitNGaussian(gauss_args):

    readfile = pt(gauss_args["peakFilename"])
    norm_method = gauss_args["normMethod"]
    print(f"Norm_method: {norm_method}\n")

    wn, inten = read_dat_file(readfile, norm_method)
    print(f"Read data:\nwn: {wn.min():.2f} - {wn.max():.2f}\n")

    output_filename = gauss_args["output_name"]
    fullfiles = [pt(i).stem for i in gauss_args["felixfiles"]]
    if output_filename == "averaged": line_color = "black"
    else:
        index = fullfiles.index(output_filename)
        index = 2*index
        if index > len(colors): 
            index = (index - len(colors)) - 1
            line_color = f"rgb{colors[index]}"
        else: line_color = f"rgb{colors[index]}"

    if "index" in gauss_args.keys():
    
        start_wn, end_wn = gauss_args["index"]
    
        print(f"Selecting data from {start_wn:.2f} - {end_wn:.2f}\n")
        index = np.logical_and(wn > start_wn, wn < end_wn)
        wn = wn[index]
        inten = inten[index]
        print(f"Processed data:\nwn: {wn.min():.2f} - {wn.max():.2f}\n")
    init_guess = list(gauss_args["fitNGauss_arguments"].values())
    N = int(len(init_guess)/3)
    print(f"NGaussian: {N}\nInitialGuess: {init_guess}\n\n")

    gfn = generateNGaussian(N)
    popt_Ngauss, pcov_Ngauss = curve_fit(gfn, wn, inten, p0=init_guess)
    
    perr_Ngauss = np.sqrt(np.diag(pcov_Ngauss))

    popt_Ngauss_ = popt_Ngauss.reshape(N, 3)
    perr_Ngauss_ = perr_Ngauss.reshape(N, 3)

    print(f"\nFitted Parameters: {popt_Ngauss_}\nCovarience: {perr_Ngauss_}\n")

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


if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))

    print(f"Received args: {args}, {type(args)}\n")
    
    fitNGaussian(args)