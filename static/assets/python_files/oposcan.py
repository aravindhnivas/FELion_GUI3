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

from FELion_sa import SpectrumAnalyserCalibrator

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

    def val(self, x): return self.f(x)

def export_file(wn, inten, fname):
    filename = f"../EXPORT/{fname}.dat"
    with open(filename, 'w+') as f:
        f.write("#NormalisedWavelength(cm-1)\t#RelativeDepletion(%)\n")
        for i in range(len(wn)):
            f.write(f"{wn[i]}\t{inten[i]}\n")

def binning(xs, ys, delta=0.2):

        delta = delta
        """
        Binns the data provided in xs and ys to bins of width delta
        output: binns, intensity 
        """

        # bins = np.arange(start, end, delta)
        # occurance = np.zeros(start, end, delta)
        BIN_STEP = delta
        BIN_START = xs.min()
        BIN_STOP = xs.max()

        indices = xs.argsort()
        datax = xs[indices]
        datay = ys[indices]

        # print("In total we have: ", len(datax), ' data points.')
        # do the binning of the data
        bins = np.arange(BIN_START, BIN_STOP, BIN_STEP)
        # print("Binning starts: ", BIN_START,
        #    ' with step: ', BIN_STEP, ' ENDS: ', BIN_STOP)
        bin_i = np.digitize(datax, bins)

        bin_a = np.zeros(len(bins) + 1)
        
        bin_occ = np.zeros(len(bins) + 1)
        for i in range(datay.size):

            bin_a[bin_i[i]] += datay[i]
            bin_occ[bin_i[i]] += 1

        binsx, data_binned = [], []
        for i in range(bin_occ.size - 1):
            if bin_occ[i] > 0:
                binsx.append(bins[i] - BIN_STEP / 2)
                data_binned.append(bin_a[i] / bin_occ[i])

        # non_zero_i = bin_occ > 0
        # binsx = bins[non_zero_i] - BIN_STEP/2
        # data_binned = bin_a[non_zero_i]/bin_occ[non_zero_i]

        return binsx, data_binned

def opoplot(opofiles, tkplot, delta, calibValue, calibFile):
    os.chdir(opofiles[0].parent)

    if tkplot:
        widget = FELion_Tk(title="OPO Spectrum", location=opofiles[0].parent)
        fig, canvas = widget.Figure()
        ax = widget.make_figure_layout(title="OPO Spectrum", xaxis="Wavenumber (cm-1)", yaxis="Intensity", savename="OPOspectrum")
    data = {"real":{}, "relative":{}, "SA":{}}
    xs, ys = [], []
    c = 0
    group = 0

    if calibFile != "": calibFile = pt(f"./{calibFile}")
    else: calibFile = pt("None")
    if calibFile.exists():
        calibdata = np.genfromtxt(calibFile).T
        # wavemeterCalib_air = 9396.929143696187
        wavemeterCalib_vaccum = 9394.356278462961
        calibdata -= wavemeterCalib_vaccum

        saCal = SpectrumAnalyserCalibrator(data=calibdata, manual=True)

        setwn, getwn = calibdata
        data["SA"]["Calibration"] = {
            "x": list(setwn),
            "y": list(getwn),
            "name": f"Calibration", "mode": "markers", "line": {"color": f"rgb{colors[0]}"}, "legendgroup": f'group0'
        }
    for i, opofile in enumerate(opofiles):

        basefile = opofile.parent / f"{opofile.stem}.obase"
        wn, counts = np.genfromtxt(opofile).T

        baseCal = BaselineCalibrator(basefile)
        
        baseCounts = baseCal.val(wn)
        ratio = counts/baseCounts

        relative_depletion =(1-ratio)*100
        label = f"{opofile.name}"
        if calibFile.exists(): wn = saCal.sa_cm(wn)
        xs = np.append(xs, wn)
        ys = np.append(ys, relative_depletion)
        export_file(wn, relative_depletion, opofile.stem)

        if tkplot: ax.plot(wn, relative_depletion, label=label)

        else: 
            data["real"][opofile.name] = {

                "x": list(wn), "y": list(counts), "name": label, "mode": "lines", "showlegend": True, "legendgroup": f'group{i}', "line": {"color": f"rgb{colors[c]}"},
            }
            
            data["real"][f"{opofile.name}_line"] = {"x": list(wn), "y": list(baseCounts), "mode": "lines", "name": f"{opofile.name}_line",
                "marker": {"color": "black"}, "legendgroup": f'group{i}', "showlegend": False
                
            }

            data["relative"][opofile.name] = {
                "x": list(wn), "y": list(relative_depletion), "name": label, "showlegend": True, 
                "fill": 'tozeroy', "mode": "lines+markers","line": {"color": f"rgb{colors[c]}"}
            }

            c += 2
            group += 1

            if c >= len(colors): c = 1

    binx, biny = binning(xs, ys, delta)
    export_file(binx, biny, "averaged")


    if not tkplot: 

        data["relative"]["averaged"] = {
            "x": list(binx), "y": list(biny), "name": f"averaged: delta={delta}", "showlegend": True, 
            "fill": 'tozeroy', "mode": "lines+markers","line": {"color": "black"}
            
        }

        if calibFile.exists():
            X = np.arange(setwn.min(), setwn.max(), 1)

            data["SA"][f"Calibration_fit"] = {
                "x": list(X),
                "y": list(saCal.sa_cm(X)),
                "name": f"Calibration_fit",
                "type": "scatter", "line": {"color": "black"},
                "showlegend": True,
                "legendgroup": f'group0'

            }

        sendData(data)

    else:
        ax.plot(binx, biny, "k.-", label=f"Averaged: delta={delta}")
        widget.plot_legend = ax.legend()
        widget.mainloop()
    
if __name__ == "__main__":
    
    args = sys.argv[1:][0].split(",")
    print(args)
    
    opofiles = [pt(i) for i in args[:-4]]
    tkplot = (False, True)[args[-4] == "plot"]
    delta = float(args[-3])
    calibValue = float(args[-2])

    calibFile = args[-1]

    print(calibValue)

    opoplot(opofiles, tkplot, delta, calibValue, calibFile)