
from pathlib import Path as pt
import numpy as np
from felionlib.utils.FELion_definitions import sendData
from felionlib.utils.FELion_constants import colors

def main(args):
    
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

    sendData(dataToSend, calling_file=pt(__file__).stem)
    