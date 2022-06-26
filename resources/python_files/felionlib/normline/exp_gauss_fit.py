
# Importing Modules
from pathlib import Path as pt
import numpy as np
from felionlib.utils.FELion_definitions import (
    gauss_fit,
    read_dat_file, sendData
)

from felionlib.utils.FELion_constants import colors

def gaussian(x, amp, sig, cen): return amp*np.exp(-0.5*((x-cen)/sig)**2)

def main(args, getvalue=False):

    norm_method = args["normMethod"]
    overwrite = args["overwrite_expfit"]
    start_wn, end_wn = args["index"]
    location = pt(args["location"])

    # Reading file
    
    fullfiles = [pt(i) for i in args["fullfiles"]]
    felix = True

    for i, f in enumerate(fullfiles):
    
        if f.stem == args["output_name"]:
    
            filename = fullfiles[i]
            line_color = "black" if f.stem == "averaged" else f"rgb{colors[2*i]}"
            extname = filename.suffix.split(".")[1]

            if "felix" in extname or filename.stem == "averaged":
            
                print("Reading felix file\n", flush=True)
                location = pt(args["location"])
                datfile_location = location.parent / "EXPORT" if location.name == "DATA" else location / "EXPORT"
            
                readfile = f"{datfile_location}/{f.stem}.dat"
                wn, inten = read_dat_file(readfile, norm_method)

            else:

                felix = False
                datfile_location = location

                print("Reading added file\n", flush=True)
                
                col = np.array(args["addedFileCol"].split(", "), dtype=int)
                scale = float(args["addedFileScale"])
                wn, inten = np.genfromtxt(f).T[col]
                inten *= scale
            
            print(
                f"Read {filename.name} from \n{filename.parent}\nwn range: {wn.min():.2f} - {wn.max():.2f}\n", flush=True
            )

            break
    
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


    dataToSend = {
        "freq": f"{uline_freq.nominal_value:.2f}", "table": f"{uline_freq:.2uP}, {uamplitude:.2uP}, {ufwhm:.2uP}, {usigma:.2uP}", 
        "for_weighted_error": f"{uline_freq.nominal_value}, {uline_freq.std_dev}, {uamplitude.nominal_value}, {uamplitude.std_dev}, {ufwhm.nominal_value}, {ufwhm.std_dev}, {usigma.nominal_value}, {usigma.std_dev}",
        "fit": {"x":list(wn), "y":list(fit_data), "name":f"{uline_freq:.2uP}; A: {uamplitude:.2uP}, {_del}: {ufwhm:.2uP}", "mode": "lines", "line": {"color":line_color}},

        "line": [
            {"type":"line", "x0":line_freq_fit, "x1":line_freq_fit, "y0":0, "y1":amplitude, "line":{"color":line_color}},
            {"type":"line", "x0":line_freq_fit-fwhm/2, "x1":line_freq_fit+fwhm/2, "y0":amplitude/2, "y1":amplitude/2, "line":{"color":line_color, "dash":"dot"}}
        ],

        "annotations": {
            "x": uline_freq.nominal_value, "y": uamplitude.nominal_value, "xref": 'x', "yref": 'y', "text": f'{uline_freq:.2uP}', "font":{"color":line_color}, "arrowcolor":line_color, "showarrow": True, "arrowhead": 2, "ax": -25, "ay": -40
        }

    }
    
    if getvalue: 
        return dataToSend, uline_freq, usigma, uamplitude, ufwhm, line_color

    expfile = datfile_location/f"{filename.stem}_{norm_method}.expfit"
    fullfit_file = datfile_location/f"{filename.stem}_{norm_method}.fullfit"
    
    if args["writeFile"]:

        print("Writing file")

        if not expfile.exists():
            with open(expfile, 'w+') as f: 
                f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")

        with open(expfile, ("a+", "w+")[overwrite]) as f:
            if overwrite: 
                f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")
            
            f.write(f"{line_freq_fit:.4f}\t{uline_freq.std_dev:.4f}\t{sigma:.4f}\t{usigma.std_dev:.4f}\t{fwhm:.4f}\t{ufwhm.std_dev:.4f}\t{amplitude:.4f}\t{uamplitude.std_dev:.4f}\n")
                
        with open(fullfit_file, ("a+", "w+")[overwrite]) as f:
            for _wn, _inten in zip(wn, fit_data): f.write(f"{_wn:.4f}\t{_inten:.4f}\n")
        
        writeFileName = pt(args["writeFileName"]).stem
        
        if writeFileName != "":
            print(f"Writing custom file {writeFileName}")
            writeFileName_expfile = datfile_location/f"{writeFileName}_{norm_method}.expfit"

            with open(expfile, "r") as f: 
                fileread = f.readlines() 
            with open(writeFileName_expfile, "w+") as f: 
                f.writelines(fileread)

            writeFileName_fullfit = datfile_location/f"{writeFileName}_{norm_method}.fullfit"
            
            with open(fullfit_file, "r") as f: 
                fileread = f.readlines()

            with open(writeFileName_fullfit, "w+") as f:
                f.writelines(fileread)

            if felix:
                writeFileName_datfile = datfile_location/f"{writeFileName}.dat"
                datfile = datfile_location/f"{filename.stem}.dat"

                with open(datfile, "r") as f: dat_read = f.readlines() 
                with open(writeFileName_datfile, "w+") as f: f.writelines(dat_read)

    sendData(dataToSend, calling_file=pt(__file__).stem)

    