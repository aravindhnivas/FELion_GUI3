
# Importing Modules
from pathlib import Path as pt
import sys

# Data analysis
import numpy as np

# FELion module
from FELion_definitions import gauss_fit, read_dat_file
from FELion_constants import colors 
from FELion_definitions import sendData

def exp_fit(location, norm_method, start_wn, end_wn, output_filename, 
    overwrite=False, fullfiles=None, tkplot=False, getvalue=False):
    

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
    
    model = gauss_fit(wn, inten)
    fit_data, uline_freq, usigma, uamplitude, ufwhm = model.get_data()

    line_freq_fit = model.get_value(uline_freq)
    fwhm = model.get_value(ufwhm)
    amplitude = model.get_value(uamplitude)
    sigma = model.get_value(usigma)

    data = {
        "freq":f"{uline_freq.nominal_value:.2f}", "table": f"{uline_freq:.2uP}, {uamplitude:.2uP}, {ufwhm:.2uP}, {usigma:.2uP}", 
        "for_weighted_error":f"{uline_freq.nominal_value}, {uline_freq.std_dev}, {uamplitude.nominal_value}, {uamplitude.std_dev}, {ufwhm.nominal_value}, {ufwhm.std_dev}, {usigma.nominal_value}, {usigma.std_dev}",
        "fit": {"x":list(wn), "y":list(fit_data), "name":f"{uline_freq:.2uP}; A: {uamplitude:.2uP}, {_del}: {ufwhm:.2uP}", "mode": "lines", "line": {"color":line_color}},
        "line": [
            {"type":"line", "x0":line_freq_fit, "x1":line_freq_fit, "y0":0, "y1":amplitude, "line":{"color":line_color}},
            {"type":"line", "x0":line_freq_fit-fwhm/2, "x1":line_freq_fit+fwhm/2, "y0":amplitude/2, "y1":amplitude/2, "line":{"color":line_color, "dash":"dot"}}
        ],
        "annotations": {

            "x": uline_freq.nominal_value, "y": uamplitude.nominal_value, "xref": 'x', "yref": 'y', "text": f'{uline_freq:.2uP}', "font":{"color":line_color}, "arrowcolor":line_color,
            "showarrow": True, "arrowhead": 2, "ax": -25, "ay": -40
        }

    }
    
    if getvalue: 
        return data, uline_freq, usigma, uamplitude, ufwhm, line_color

    filename = f"{output_filename}_{norm_method}.expfit"
    expfile = datfile_location/filename
    
    if not expfile.exists():
        with open(expfile, 'w+') as f:
            f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")
            
    with open(expfile, ("a+", "w+")[overwrite]) as f:

        if overwrite: f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")
        f.write(f"{line_freq_fit:.4f}\t{uline_freq.std_dev:.4f}\t{sigma:.4f}\t{usigma.std_dev:.4f}\t{fwhm:.4f}\t{ufwhm.std_dev:.4f}\t{amplitude:.4f}\t{uamplitude.std_dev:.4f}\n")
    sendData(data)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    print(f"Received args: {args}")
    fullfiles = [pt(i).stem for i in args[0:-6]]

    start_wn = float(args[-2])
    end_wn = float(args[-1])

    location = pt(args[-3])
    
    norm_method = args[-4]
    output_filename = args[-5]
    overwrite = args[-6]

    if overwrite == "true": overwrite = True
    else: overwrite = False
    exp_fit(location, norm_method, start_wn, end_wn, output_filename, overwrite, fullfiles)