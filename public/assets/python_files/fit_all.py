
# Importing built-in modules
import numpy as np
from scipy.signal import find_peaks as peak
from pathlib import Path as pt
import json, sys


from FELion_definitions import read_dat_file
from FELion_widgets import FELion_Tk
from FELion_constants import colors 
from FELion_definitions import sendData

from exp_gauss_fit import exp_fit

def fit_all_peaks(filename, norm_method, prominence=None, width=None, height=None, fitall=False, overwrite=False, tkplot=False, fullfiles=None):

    wn, inten = read_dat_file(filename, norm_method)

    if tkplot:
        widget = FELion_Tk(title=f"Fitted: {filename.name}", location=filename.parent.parent / "OUT")
        fig, canvas = widget.Figure()

        if norm_method == "Relative": ylabel = "Relative Depletion (%)"
        else: ylabel =  "Norm. Intensity"
        ax = widget.make_figure_layout(title=f"Experimental fitted Spectrum: {filename.name}", xaxis="Wavenumber $(cm^{-1})$", yaxis=ylabel, yscale="linear", savename=f"{filename.stem}_expfit")
        ax.plot(wn, inten, ".", label=filename.name)

    indices, _ = peak(inten, prominence=prominence, width=width, height=height)

    _["wn_range"] = np.array([wn[_["left_bases"]], wn[_["right_bases"]]]).T

    for item in _:
        _[item] = _[item].tolist()
    wn_ = list(wn[indices])
    inten_ = list(inten[indices])
    
    data = {"data": {}, "extras": _, "annotations":{}}

    if filename.stem == "averaged": line_color = "black"
    else:
        index = fullfiles.index(filename.stem)
        line_color = f"rgb{colors[2*index]}"

    data["data"] = {
        "x":wn_, "y":inten_, "name":"peaks", "mode":"markers",
        "marker":{
            "color":"blue", "symbol": "star-triangle-up", "size": 12
        }
    }

    data["annotations"] = [
            {
            "x": x,
            "y": y,
            "xref": 'x',
            "yref": 'y',
            "text": f'{x:.2f}',
            "showarrow": True,
            "arrowhead": 2,
            "ax": -25,
            "ay": -40,
            "font":{"color":line_color}, "arrowcolor":line_color
            
        }
        for x, y in zip(wn_, inten_)
    ]
    dataToSend = [{"data": data["data"]}, {"extras":data["extras"]}, {"annotations":data["annotations"]}]

    if not fitall: sendData(dataToSend)
    else:

        location = filename.parent.parent
        output_filename = filename.stem

        fit_data = [{"data": data["data"]}, {"extras":data["extras"]}]

        filename = f"{output_filename}.expfit"
        datfile_location = location/"EXPORT"
        expfile = datfile_location/filename

        if overwrite: method = "w"
        else: method = "a"
        annotations = []
        get_data = []

        with open(expfile, method) as f:
            if overwrite: f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")

            for wavelength in _["wn_range"]:

                get_data_temp, uline_freq, usigma, uamplitude, ufwhm, line_color = exp_fit(location, norm_method, wavelength[0], wavelength[1], output_filename, getvalue=True, fullfiles=fullfiles)
                if uline_freq.nominal_value < 0 or ufwhm.nominal_value > 100: continue
                if tkplot:

                    print("Fitting for wavelength range: ", wavelength[0], wavelength[1])
                    ax.plot(get_data_temp["fit"]["x"], get_data_temp["fit"]["y"], "k-", label=get_data_temp["fit"]["name"])
                    xcord, ycord = uline_freq.nominal_value, uamplitude.nominal_value
                    text_frac = 0.01

                    ax.annotate(f'{uline_freq:.2uP}', xy=(xcord, ycord), xycoords='data',
                                xytext=(xcord+xcord*text_frac, ycord+ycord*text_frac), textcoords='data',
                                arrowprops=dict(arrowstyle="->", connectionstyle="arc3")
                    )
                else:
                    annotate = {
                        "x": uline_freq.nominal_value, "y": uamplitude.nominal_value, "xref": 'x', "yref": 'y', "text": f'{uline_freq:.2uP}', "font":{"color":line_color},
                        "arrowcolor":line_color, "showarrow": True, "arrowhead": 2, "ax": -25, "ay": -40
                    }
                    annotations.append(annotate)
                    get_data.append(get_data_temp)
                    f.write(f"{uline_freq.nominal_value:.4f}\t{uline_freq.std_dev:.4f}\t{usigma.nominal_value:.4f}\t{usigma.std_dev:.4f}\t{ufwhm.nominal_value:.4f}\t{ufwhm.std_dev:.4f}\t{uamplitude.nominal_value:.4f}\t{uamplitude.std_dev:.4f}\n")
                
        if tkplot:
            widget.plot_legend = ax.legend()
            widget.mainloop()
            
        else:

            fit_data.append({"annotations":annotations})
            fit_data.append(get_data)
            
            sendData(fit_data)
        
if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    filename = args[0]
    location = pt(args[1])
    if location.name == "DATA": location = location.parent
    filename = location / f"EXPORT/{filename}.dat"

    norm_method = args[2]

    prominence = args[3]
    if prominence == "": prominence = None
    else: prominence = float(prominence)

    fitall = args[4]
    if fitall == "true": fitall = True
    else: fitall = False

    width = args[5]
    if width == "": width = None
    else: width = float(width)

    height = args[6]
    if height == "": height = None
    else: height = float(height)


    overwrite = args[7]
    if overwrite == "true": overwrite = True
    else: overwrite = False

    tkplot = args[8]
    if tkplot == "true": tkplot = True
    else: tkplot = False

    fullfiles = [pt(i).stem for i in args[9:]]
    
    fit_all_peaks(filename, norm_method, prominence, width, height, fitall, overwrite, tkplot, fullfiles)