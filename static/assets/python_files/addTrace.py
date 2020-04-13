# Built-in
import os, json, sys
from pathlib import Path as pt

# DATA Analysis
import numpy as np


# FELion modules
from FELion_definitions import sendData
from FELion_constants import colors


def addTraceToPlot(args):
    files = [pt(f) for f in args["files"]]
    col = np.array(args["col"].split(", "), dtype=int)

    scale = float(args["scale"])
    print(f"Files: {files}\nCol: {col}")

    c = int(args["N"]) + 2
    dataToSend = []
    for f in files:
        x, y = np.genfromtxt(f).T[col]
        y *= scale

        data = {
            "x": list(x),
            "y": list(y),
            "name": f"{f.name}",
            "fill": 'tozeroy',
            "mode": "lines+markers",
            "line": {"color": f"rgb{colors[c]}"},
            "marker": {"size":1}

        }

        c +=2

        dataToSend.append(data)
        print(data)
    sendData(dataToSend)

if __name__ == "__main__":
    
    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")

    addTraceToPlot(args)