
# Importing built-in modules
import numpy as np
from pathlib import Path as pt
from scipy.signal import find_peaks as peak
from felionlib.utils.FELion_constants import colors
from felionlib.utils.FELion_definitions import read_dat_file, sendData

def main(args):

    norm_method = args["normMethod"]
    prominence = args["peak_prominence"]

    width = args["peak_width"]
    height = args["peak_height"]
    start_wn, end_wn = args["selectedIndex"]
    
    # Reading file
    fullfiles = [pt(i) for i in args["fullfiles"]]
    for i, f in enumerate(fullfiles):
    
        if f.stem == args["output_name"]:

            filename = fullfiles[i]
            if f.stem == "averaged": line_color = "black"
            else: line_color = f"rgb{colors[2*i]}"
            extname = filename.suffix.split(".")[1]
            if "felix" in extname or filename.stem == "averaged":
                print("Reading felix file\n")
                location = pt(args["location"])

                if location.name == "DATA": location = location.parent

                filename = location / f"EXPORT/{filename.stem}.dat"

                wn, inten = read_dat_file(filename, norm_method)
            else:
                print("Reading added file\n")
                col = np.array(args["addedFileCol"].split(", "), dtype=int)
                scale = float(args["addedFileScale"])
                wn, inten = np.genfromtxt(f).T[col]
                inten *= scale
            
            print(f"Read {filename.name} from \n{filename.parent}\nwn range: {wn.min():.2f} - {wn.max():.2f}\n")

            break

    if start_wn > 0:

        print(f"Selecting data from {start_wn} - {end_wn}\n")
        index = np.logical_and(wn > start_wn, wn < end_wn)
    
        wn = wn[index]
        inten = inten[index]
        print(f"Processed data:\nwn: {wn.min():.2f} - {wn.max():.2f}")
        
    indices, _ = peak(inten, prominence=prominence, width=width, height=height)
    _["wn_range"] = np.array([wn[_["left_bases"]], wn[_["right_bases"]]]).T
    for item in _: _[item] = _[item].tolist()

    wn_ = [round(i, 2) for i in wn[indices]]

    inten_ = [round(i, 2) for i in inten[indices]]

    data = {"data": {}, "extras": _, "annotations":{}}


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

    sendData(dataToSend, calling_file=pt(__file__).stem)