# Importing Modules
from pathlib import Path as pt
import sys

# Data analysis
import numpy as np
from scipy.optimize import curve_fit

# FELion module
from FELion_definitions import gauss_fit, read_dat_file
from FELion_constants import colors 
from FELion_definitions import sendData

def _2gaussian(x, amp1,cen1,sigma1, amp2,cen2,sigma2):
    return amp1*(np.exp((-1.0/2.0)*(((x-cen1)/sigma1)**2))) + \
            amp2*(np.exp((-1.0/2.0)*(((x-cen2)/sigma2)**2)))

def exp_fit(location, norm_method, start_wn, end_wn, output_filename, overwrite, fullfiles, amp1, amp2, cen1, cen2, sig1, sig2, tkplot=False):
    
    if location.name is "DATA": datfile_location = location.parent/"EXPORT"
    else: datfile_location = location/"EXPORT"
    readfile = f"{datfile_location}/{output_filename}.dat"
    wn, inten = read_dat_file(readfile, norm_method)

    if output_filename == "averaged": line_color = "black"
    else:
        index = fullfiles.index(output_filename)
        index = 2*index
        if index > len(colors): 
            index = (index - len(colors)) - 1
            line_color = f"rgb{colors[index]}"
        else: line_color = f"rgb{colors[index]}"

    index = np.logical_and(wn > start_wn, wn < end_wn)
    wn = wn[index]
    inten = inten[index]

    _sig = "\u03C3"
    _del = "\u0394"
    
    popt_2gauss, pcov_2gauss = curve_fit(_2gaussian, wn, inten, p0=[amp1, cen1, sig1, amp2, cen2, sig2])

    perr_2gauss = np.sqrt(np.diag(pcov_2gauss))
    pars_1 = popt_2gauss[0:3]
    pars_2 = popt_2gauss[3:6]

    gauss_peak = _2gaussian(wn, *popt_2gauss)


    data = {
        "peak": {"x":list(wn), "y":list(gauss_peak), "name":f"{popt_2gauss}", "mode": "lines", "line": {"color":line_color}},
    }

    sendData(data)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    print(f"Received args: {args}")

    fullfiles = [pt(i).stem for i in args[6:-6]]

    start_wn = float(args[-2])
    end_wn = float(args[-1])
    location = pt(args[-3])
    norm_method = args[-4]

    output_filename = args[-5]

    overwrite = args[-6]

    amp1, amp2, cen1, cen2, sig1, sig2 = [float(i) for i in args[:6]]

    if overwrite == "true": overwrite = True
    else: overwrite = False

    exp_fit(location, norm_method, start_wn, end_wn, output_filename, overwrite, fullfiles, amp1, amp2, cen1, cen2, sig1, sig2)