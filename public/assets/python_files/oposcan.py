# System modules
import sys, json, os, traceback
from pathlib import Path as pt

# Data analysis
import numpy as np
from scipy.interpolate import interp1d

# FELion tkinter figure module
from FELion_widgets import FELion_Tk
from FELion_constants import colors
from FELion_definitions import sendData

def ReadBase(basefile):

    data = np.genfromtxt(basefile)
    xs, ys = data[:,0], data[:,1]
    with open(basefile, 'r') as f: interpol = f.readlines()[1].strip().split('=')[-1]

    return xs, ys, interpol

class BaselineCalibrator(object):
    def __init__(self, basefile, ms=None):
        self.ms = ms
        self.Bx, self.By, self.interpol = ReadBase(basefile)
        self.f = interp1d(self.Bx, self.By, kind=self.interpol)

    def val(self, x):
        return self.f(x)

def opoplot(opofiles, tkplot):

    if tkplot:
        
        widget = FELion_Tk(title="Mass spectrum", location=opofiles[0].parent)

        fig, canvas = widget.Figure()

        if len(opofiles) == 1: savename=opofiles[0].stem
        else: savename = "combined_masspec"
        ax = widget.make_figure_layout(title="Mass Spectrum", xaxis="Mass [u]", yaxis="Counts", yscale="log", savename=savename)

    else: data = {"real":{}, "relative":{}}
    
    c = 0
    for i, opofile in enumerate(opofiles):
        basefile = opofile.parent / f"{opofile.stem}.obase"
        wn, counts = np.genfromtxt(opofile).T
        baseCal = BaselineCalibrator(basefile)

        baseCounts = baseCal.val(wn)
        ratio = counts/baseCounts
        relative_depletion =(1-ratio)*100
        label = f"{opofile.name}"
        if tkplot: ax.plot(wn, counts, label=label)
        else: 

            
            data["real"][opofile.name] = {
                "x": list(wn), "y": list(counts), "name": label, "mode": "lines", "showlegend": True, "legendgroup": f'group{i}', "line": {"color": f"rgb{colors[c]}"},
            }
            
            data["real"][f"{opofile.name}_line"] = {
                "x": list(wn), "y": list(baseCounts), "mode": "lines", "name": f"{opofile.name}_line",
                "marker": {"color": "black"}, "legendgroup": f'group{i}', "showlegend": False,
            }

            data["relative"][opofile.name] = {
                "x": list(wn), "y": list(relative_depletion), "name": label, "mode": "lines", "showlegend": True, "line": {"color": f"rgb{colors[c]}"}
            }

            c += 2
            if c >= len(colors): c = 1

    if not tkplot:
        
        sendData(data)
    else:
        widget.plot_legend = ax.legend()

        widget.mainloop()

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    opofiles = [pt(i) for i in args[:-1]]

    tkplot = args[-1]
    if tkplot == "plot": tkplot = True
    else: tkplot = False
    # print(args)
    opoplot(opofiles, tkplot)