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
    return popt_Ngauss, perr_Ngauss, gfn
    
def fitNGaussian(gauss_args):

    # Collected parameters
    # readfile = pt(gauss_args["peakFilename"])
    output_filename = gauss_args["output_name"]
    readfile = pt(gauss_args["location"]).parent / f"EXPORT/{output_filename}.dat"
    norm_method = gauss_args["normMethod"]

    # Reading file

    felix = True
    fullfiles = [pt(i) for i in gauss_args["fullfiles"]]

    for i, f in enumerate(fullfiles):
    
        if f.stem == gauss_args["output_name"]:

            filename = fullfiles[i]
            if f.stem == "averaged": line_color = "black"
            else: line_color = f"rgb{colors[2*i]}"
            extname = filename.suffix.split(".")[1]
            if "felix" in extname or filename.stem == "averaged":
                print("Reading felix file\n")
                location = pt(gauss_args["location"])

                if location.name == "DATA": location = location.parent

                filename = location / f"EXPORT/{filename.stem}.dat"
                wn, inten = read_dat_file(filename, norm_method)
            else:

                felix = False
                print("Reading added file\n")
                col = np.array(gauss_args["addedFileCol"].split(", "), dtype=int)
                scale = float(gauss_args["addedFileScale"])
                wn, inten = np.genfromtxt(f).T[col]
                inten *= scale
            print(f"Read {filename.name} from \n{filename.parent}\nwn range: {wn.min():.2f} - {wn.max():.2f}\n")
            
            break
    index = False
    if "index" in gauss_args: 
        index = start_wn, end_wn = gauss_args["index"]
        print(f"Selecting data from {start_wn} - {end_wn}\n")
        ind = np.logical_and(wn > start_wn, wn < end_wn)
        wn = wn[ind]
        inten = inten[ind]
        
        print(f"Processed data:\nwn: {wn.min():.2f} - {wn.max():.2f}")

    # Get peak index to plot for other normMethods
    fit_guesses = gauss_args["fitNGauss_arguments"]
    wn_found_peaks = [fit_guesses[key] for key in fit_guesses.keys() if key.startswith("cen")]
    filtered_index = np.in1d(wn, wn_found_peaks)

    # Initialising for data to send
    _sig, _del  = "\u03C3",  "\u0394"
    fwhm = lambda usigma: 2*usigma*np.sqrt(2*np.log(2))
    dataTosend = {}
    
    datfile = readfile.parent/f"{output_filename}.dat"
    
    overwrite = gauss_args["overwrite_expfit"]
    
    if felix: normMethods = ["Relative", "Log", "IntensityPerPhoton"]
    else: normMethods = ["addedFile"]
    # Fitting for all norm intensity methods
    for method in normMethods:
        
        print(f"Fitting for method: {method}\n")

        # Reading datfile
        if felix: _wn, _inten = filterWn(datfile, method, index)
        else: _wn, _inten = wn, inten
        
        # Getting data from peak index
        _guess_inten = _inten[filtered_index]
        print(f"Guessed Intesity: {_guess_inten}\n")
        
        # Modifing fit init guess from peak index guess
        for i, guess_amp in enumerate(_guess_inten): fit_guesses[f"A{i}"] = guess_amp
        
        # New init guess
        init_guess = list(fit_guesses.values())
        N = int(len(init_guess)/3)
        
        # Fitting
        popt_Ngauss, perr_Ngauss, gfn = fitNGauss(init_guess, _wn, _inten)
        
        # Simulation data from fitted curve
        sim_inten = gfn(_wn, *popt_Ngauss)

        # Reshaping fitted parameter (freq, amp, sigma)
        popt_Ngauss = popt_Ngauss.reshape(N, 3)
        perr_Ngauss = perr_Ngauss.reshape(N, 3)

        # Send json data to program
        
        if norm_method == method or method == "addedFile":

            dataTosend["fitted_data"] = { "x":list(_wn), "y":list(sim_inten),  "mode": "lines", "name":f"{N} Gaussian", "line": {"color":line_color} }
            dataTosend["fitted_parameter"] = [
                { "freq": f"{uf(fit[0], err[0]):.2uP}", "amp":f"{uf(fit[1], err[1]):.2uP}", "sig":f"{uf(fit[2], err[2]):.2uP}", "fwhm":f"{fwhm(uf(fit[2], err[2])):.2uP}"}
                for fit, err in zip(popt_Ngauss, perr_Ngauss)
            ]


            dataTosend["for_weighted_error"] = [
                f"{fit[0]}, {err[0]}, {fit[1]}, {err[1]}, {fwhm(uf(fit[2], err[2])).nominal_value}, {fwhm(uf(fit[2], err[2])).std_dev}, {fit[2]}, {err[2]}"
                for fit, err in zip(popt_Ngauss, perr_Ngauss)
            ]
            
            sendData(dataTosend)
        
        # Writing fullfit and expfit files
        
        _fitted_freq = np.array([popt_Ngauss, perr_Ngauss]).T[0]
        _fitted_inten = np.array([popt_Ngauss, perr_Ngauss]).T[1]
        _fitted_sigma = np.array([popt_Ngauss, perr_Ngauss]).T[2]

        # Filenames
        expfile = readfile.parent/f"{output_filename}_{method}.expfit"
        fitfile = readfile.parent/f"{output_filename}_{method}.fullFit"
        
        if felix: 
            with open(datfile, "r") as f: writeFileName_datfile = f.readlines() 
        if gauss_args["writeFile"]:

            print("Writing file")
            with open(fitfile, ("a+", "w+")[overwrite]) as f:
                if overwrite: f.write(f"#Wn(cm-1)\tIntensity\n")
                for freq, inten in zip(_wn, sim_inten): f.write(f"{freq:.4f}\t{inten:.4f}\n")
        
            with open(expfile, ("a+", "w+")[overwrite]) as f:

                if overwrite: 
                    f.write(f"#Frequency\tFreq_err\t#Intensity({method})\t#Intensity_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\n")
                fitted = np.array([_fitted_freq, _fitted_inten, _fitted_sigma])

                for freq, amp, sigma in zip(*fitted):

                    _fwhm = fwhm(uf(sigma[0], sigma[1]))
                    _fwhm = [_fwhm.nominal_value, _fwhm.std_dev]
                    if _fwhm[0] > 500: continue

                    f.write(f"{freq[0]:.4f}\t{freq[1]:.4f}\t{amp[0]:.4f}\t{amp[1]:.4f}\t{sigma[0]:.4f}\t{sigma[1]:.4f}\t{_fwhm[0]:.4f}\t{_fwhm[1]:.4f}\n")

            writeFileName = gauss_args["writeFileName"]
            if writeFileName != "":

                print(f"Writing custom file {writeFileName}")
                writeFileName_expfile = readfile.parent/f"{writeFileName}_{method}.expfit"
                writeFileName_fitfile = readfile.parent/f"{writeFileName}_{method}.fullFit"
                writeFileName_datfile = readfile.parent/f"{writeFileName}.dat"
                for read, write in zip([expfile, fitfile, datfile], [writeFileName_expfile, writeFileName_fitfile, writeFileName_datfile]):
                    with open(read, "r") as f: fileread = f.readlines()
                    with open(write, "w+") as f: f.writelines(fileread)


if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")
    fitNGaussian(args)