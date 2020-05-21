import sys, json
from pathlib import Path as pt

import numpy as np
from FELion_definitions import sendData, read_dat_file

def var_find(openfile):

    var = {'res': 'm03_ao13_reso', 'b0': 'm03_ao09_width', 'trap': 'm04_ao04_sa_delay'}
    with open(openfile, 'r') as f: readfile = np.array(f.readlines())
    for line in readfile:
        if not len(line.strip()) == 0 and line.split()[0] == '#':
            for j in var:
                if var[j] in line.split():
                    var[j] = float(line.split()[-3])
    res, b0, trap = round(var['res'], 2), int( var['b0']/1000), int(var['trap']/1000)

    return res, b0, trap

def get_details(args={}):

    files = [pt(f) for f in args["files"]]
    location = files[0].parent.parent
    # normMethod = args["normMethod"]
    dataToSend = {"files":[]}

    for f in files:

        res, b0, trap = var_find(f)
        datfile = location / f"EXPORT/{f.stem}.dat"
        wn = np.genfromtxt(datfile).T[0]
        _ = {"filename":f.stem, "res":round(res, 1), "b0":round(b0, 1), "trap":round(trap/1000, 1), "range": [int(wn.min()), int(wn.max())]}
        dataToSend["files"].append(_)
    sendData(dataToSend)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")
    get_details(args)