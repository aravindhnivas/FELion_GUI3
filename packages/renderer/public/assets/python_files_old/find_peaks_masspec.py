# Importing modules
import json, sys
from pathlib import Path as pt

# Data analysis
import numpy as np
from scipy.signal import find_peaks as peak

from FELion_definitions import sendData

def find_mass_peaks(filename, prominence, width, height):


    mass, counts = np.genfromtxt(filename).T
    indices, _ = peak(counts, prominence=prominence, width=width, height=height)
    mass = list(mass[indices])
    counts = list(counts[indices])
    


    annotations = [
        
        {
            "x": x,
            "y": y,
            "xref": 'x',
            "yref": 'y',
            "text": f'({x:.1f}, {y:.0f})',
            "showarrow": True,
            "arrowhead": 2,
            "ax": -25,
            "ay": -40
        }
        for x, y in zip(mass, counts)
    ]

    dataToSend = {"annotations":annotations}
    sendData(dataToSend)

if __name__ == "__main__":
    args = json.loads(sys.argv[1])
    # args = sys.argv[1:][0].split(",")

    filename = pt(args["filename"])
    prominence = float(args["peak_prominance"])
    width = float(args["peak_width"])
    height = float(args["peak_height"])
    find_mass_peaks(filename, prominence, width, height)
    