
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

def fit_all_peaks(filename, norm_method, prominence=None, width=None, height=None,  fullfiles=None, start_wn=None, end_wn=None):

    wn, inten = read_dat_file(filename, norm_method)

    print(f"Read data:\nwn: {wn.min():.2f} - {wn.max():.2f}")

    if start_wn > 0:
        print(f"Selecting data from {start_wn} - {end_wn}\n")
    
        index = np.logical_and(wn > start_wn, wn < end_wn)
    
        wn = wn[index]
        inten = inten[index]
        print(f"Processed data:\nwn: {wn.min():.2f} - {wn.max():.2f}")
        

    indices, _ = peak(inten, prominence=prominence, width=width, height=height)
    _["wn_range"] = np.array([wn[_["left_bases"]], wn[_["right_bases"]]]).T
    for item in _: _[item] = _[item].tolist()

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
            "text": f'({x:.2f}, {y:.2f})',
            "showarrow": True,
            "arrowhead": 2,
            "ax": -25,
            "ay": -40,
            "font":{"color":line_color}, "arrowcolor":line_color
        }
        for x, y in zip(wn_, inten_)
        
    ]
    dataToSend = [{"data": data["data"]}, {"extras":data["extras"]}, {"annotations":data["annotations"]}, {"filename":str(filename)}]

    sendData(dataToSend)

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

    width = args[4]
    if width == "": width = None
    else: width = float(width)

    height = args[5]
    if height == "": height = None
    else: height = float(height)

    fullfiles = [pt(i).stem for i in args[6:-2]]


    start_wn = float(args[-2])
    end_wn = float(args[-1])
    
    print(start_wn, end_wn)
    fit_all_peaks(filename, norm_method, prominence, width, height, fullfiles, start_wn, end_wn)