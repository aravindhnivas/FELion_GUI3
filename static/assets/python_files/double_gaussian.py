# Importing Modules
from pathlib import Path as pt
import sys

# Data analysis
import numpy as np
from scipy.optimize import curve_fit

from uncertainties import ufloat as uf

# FELion module
from FELion_definitions import gauss_fit, read_dat_file
from FELion_constants import colors 
from FELion_definitions import sendData

def _2gaussian(x, amp1,cen1,sigma1, amp2,cen2,sigma2):
    return amp1*(np.exp((-1.0/2.0)*(((x-cen1)/sigma1)**2))) + \
            amp2*(np.exp((-1.0/2.0)*(((x-cen2)/sigma2)**2)))

def exp_fit(location, norm_method, start_wn, end_wn, output_filename, overwrite, fullfiles, amp1, amp2, cen1, cen2, sig1, sig2, tkplot=False):
    
    if location.name == "DATA": datfile_location = location.parent/"EXPORT"
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
    
    data = wn, inten
    
    data =  np.take(data, data[1].argsort(), 1)

    if (amp1 == 0 or amp2 == 0): init = [data[1][-1], data[0][-1], 5, data[1][-5], data[0][-5], 5]
    else: init = [amp1,cen1,sig1, amp2,cen2,sig2]

    popt_2gauss, pcov_2gauss = curve_fit(_2gaussian, wn, inten, p0=init)
    perr_2gauss = np.sqrt(np.diag(pcov_2gauss))
    amp1, cen1, sig1, amp2, cen2, sig2 = popt_2gauss

    amp1_err, cen1_err, sig1_err = perr_2gauss[0:3]
    amp2_err, cen2_err, sig2_err = perr_2gauss[3:6]

    uamp1 = uf(amp1, amp1_err)
    uamp2 = uf(amp2, amp2_err)
    
    ucen1 = uf(cen1, cen1_err)
    ucen2 = uf(cen2, cen2_err)

    usig1 = uf(sig1, sig1_err)
    
    usig2 = uf(sig2, sig2_err)
    uFWHM1 = 2*np.sqrt(2*np.log(2))*usig1

    uFWHM2 = 2*np.sqrt(2*np.log(2))*usig2
    gauss_peak = _2gaussian(wn, *popt_2gauss)
    data = {
        "table": f"{ucen1:.2uP}, {uamp1:.2uP}, {usig1:.2uP}, {uFWHM1:.2uP}, {ucen2:.2uP}, {uamp2:.2uP}, {usig2:.2uP}, {uFWHM2:.2uP}",
        "peak": {"x":list(wn), "y":list(gauss_peak), "name":f"[{ucen1:.2uP}, {ucen2:.2uP}]", "mode": "lines", "line": {"color":line_color}},
        "for_weighted_error1":f"{cen1}, {cen1_err}, {amp1}, {amp1_err}, {uFWHM1.nominal_value}, {uFWHM1.std_dev}, {sig1}, {sig1_err}",
        "for_weighted_error2":f"{cen2}, {cen2_err}, {amp2}, {amp2_err}, {uFWHM2.nominal_value}, {uFWHM2.std_dev}, {sig2}, {sig2_err}",
        "annotations": [ {"x": cen1, "y": amp1, "xref": 'x', "yref": 'y', "text": f'{ucen1:.2uP}',
                "font":{"color":line_color}, "arrowcolor":line_color, "showarrow": True, "arrowhead": 2, "ax": -25, "ay": -40
            }, {"x": cen2, "y": amp2, "xref": 'x', "yref": 'y', "text": f'{ucen2:.2uP}',
                "font":{"color":line_color}, "arrowcolor":line_color, "showarrow": True, "arrowhead": 2, "ax": -25, "ay": -40
            }
        ]
    }

    filename = f"{output_filename}.expfit"
    expfile = datfile_location/filename

    if overwrite:
        with open(expfile, "w") as f:

            f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")
            f.write(f"{cen1:.4f}\t{cen1_err:.4f}\t{sig1:.4f}\t{sig1_err:.4f}\t{uFWHM1.nominal_value:.4f}\t{uFWHM1.std_dev:.4f}\t{amp1:.4f}\t{amp1_err:.4f}\n")
            f.write(f"{cen2:.4f}\t{cen2_err:.4f}\t{sig2:.4f}\t{sig2_err:.4f}\t{uFWHM2.nominal_value:.4f}\t{uFWHM2.std_dev:.4f}\t{amp2:.4f}\t{amp2_err:.4f}\n")
    else:
        with open(expfile, "a") as f:

            f.write(f"{cen1:.4f}\t{cen1_err:.4f}\t{sig1:.4f}\t{sig1_err:.4f}\t{uFWHM1.nominal_value:.4f}\t{uFWHM1.std_dev:.4f}\t{amp1:.4f}\t{amp1_err:.4f}\n")
            f.write(f"{cen2:.4f}\t{cen2_err:.4f}\t{sig2:.4f}\t{sig2_err:.4f}\t{uFWHM2.nominal_value:.4f}\t{uFWHM2.std_dev:.4f}\t{amp2:.4f}\t{amp2_err:.4f}\n")
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