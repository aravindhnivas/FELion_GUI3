# System modules
import sys
# import json
import os
from pathlib import Path as pt
# import traceback

# Data analysis
import numpy as np

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

from FELion_definitions import sendData

def var_find(massfile):

    var = {'res': 'm03_ao13_reso', 'b0': 'm03_ao09_width',
           'trap': 'm04_ao04_sa_delay'}
    with open(massfile, 'r') as mfile:
        mfile = np.array(mfile.readlines())

    for line in mfile:
        if not len(line.strip()) == 0 and line.split()[0] == '#':
            for j in var:
                if var[j] in line.split():
                    var[j] = float(line.split()[-3])

    res, b0, trap = round(var['res'], 2), int(
        var['b0']/1000), int(var['trap']/1000)
    return res, b0, trap

def massplot(massfiles, tkplot):
    os.chdir(massfiles[0].parent)
    if tkplot:
        
        widget = FELion_Tk(title="Mass spectrum", location=massfiles[0].parent)

        _ = widget.Figure()

        if len(massfiles) == 1: savename=massfiles[0].stem
        else: savename = "combined_masspec"
        ax = widget.make_figure_layout(title="Mass Spectrum", xaxis="Mass [u]", yaxis="Counts", yscale="log", savename=savename)

    else: dataToSend = {}
    for massfile in massfiles:

        masses_temp, counts_temp = np.genfromtxt(massfile).T

        res, b0, trap = var_find(massfile)
        label = f"{massfile.stem}: Res:{res}; B0: {b0}ms; trap: {trap}ms"

        if tkplot: ax.plot(masses_temp, counts_temp, label=label)
        
        else: dataToSend[massfile.stem] = {
            "x": list(masses_temp), "y": list(counts_temp), "name": label, "mode": "lines", "showlegend": True
        }

    if not tkplot:
        sendData(dataToSend, calling_file=pt(__file__).stem)

    else:
        widget.plot_legend = ax.legend()
        widget.mainloop()


# args = None
def main(args):
    # global args
    # args = arguments
    massfiles = [pt(i) for i in args["massfiles"]]
    tkplot = (False, True)[args["tkplot"] == "plot"]
    massplot(massfiles, tkplot)