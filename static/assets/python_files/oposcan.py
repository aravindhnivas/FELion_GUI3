# System modules
import sys, json, os, traceback, json
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

def export_file(fname, wn, inten, relative_depletion, energyPerPhoton):
    fileInfo = None
    if fname=="averaged":
        fileInfo = [_.name for _ in opofiles]
        fileInfo = f"# {fileInfo}\n#########################################\n\n"
    unitInfo = f"# cm-1\tNorm. Int./J\t%\tNorm. Int./photon\n"
    filename = f"EXPORT/{fname}.dat"
    with open(filename, 'w+') as f:
        
        f.write("#NormalisedWavelength(cm-1)\t#NormalisedIntensity\t#RelativeDepletion(%)\t#IntensityPerPhoton\n")
        f.write(unitInfo)
        if fileInfo is not None: f.write(fileInfo)


        for i in range(len(wn)):
            f.write(f"{wn[i]}\t{inten[i]}\t{relative_depletion[i]}\t{energyPerPhoton[i]}\n")
                
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

def makeDataToSend(x, y, name, update={}):

    return { **update, "x": list(x), "y": list(y), "name": name}

opofiles = []
def opoplot(args):

    global opofiles
    opofiles = args["opofiles"]
    opofiles = [pt(f) for f in opofiles]

    tkplot = args["tkplot"]
    if tkplot == "run": tkplot = False
    else: tkplot = True
    delta = args["deltaOPO"]
    opoPower = float(args["opoPower"])
    calibFile = args["calibFile"]
    location = pt(opofiles[0]).parent / "../"

    os.chdir(location)

    dataToSend = {"base": {}, "SA": {}, "average": {}, "average_rel": {}, "average_per_photon": {}}

    blackColor = {"color": "black"}
    
    nolegend = {"showlegend": False}

    if tkplot:
        widget = FELion_Tk(title="OPO Spectrum", location=location/"OUT")
        fig, canvas = widget.Figure()
        ax = widget.make_figure_layout(title="OPO Spectrum", xaxis="Wavenumber (cm-1)", yaxis="Intensity", savename="OPOspectrum")
    data = {"real":{}, "relative":{}, "SA":{}}
    xs, ys = [], []
    ys_r = [], []

    c = 0
    group = 0

    if calibFile != "": calibFile = pt(f"DATA/{calibFile}")
    else: calibFile = pt("None")
    
    if calibFile.exists():
        calibdata = np.genfromtxt(calibFile).T
        # wavemeterCalib_air = 9396.929143696187
        wavemeterCalib_vaccum = 9394.356278462961
        calibdata -= wavemeterCalib_vaccum

        
        
        saCal = SpectrumAnalyserCalibrator(data=calibdata, manual=True)
        
        setwn, getwn = calibdata
        X = np.arange(setwn.min(), setwn.max(), 1)

        dataToSend["SA"]["Calibration"] = makeDataToSend(setwn, getwn, "Calibration", update={"legendgroup": f'group0', "mode": "markers"})
        dataToSend["SA"][f"Calibration_fit"] = makeDataToSend(X, saCal.sa_cm(X), f"Calibration_fit", update={"mode": "lines", "line":blackColor, "legendgroup": f'group0', **nolegend})

    for i, opofile in enumerate(opofiles):

        basefile = opofile.parent / f"{opofile.stem}.obase"
        wn, counts = np.genfromtxt(opofile).T

        wn_original = np.copy(wn)
        baseCal = BaselineCalibrator(basefile)
        
        baseCounts = baseCal.val(wn)
        ratio = counts/baseCounts

        relative_depletion =(1-ratio)*100
        totalPower = opoPower * 10
        inten = (-np.log(ratio)/totalPower)*1000
        energyPerPhoton = (np.array(wn) * np.array(inten)) / 1e3

        label = f"{opofile.name}"

        if calibFile.exists(): wn = saCal.sa_cm(wn)


        xs = np.append(xs, wn)
        ys = np.append(ys, inten)
        ys_r = np.append(ys_r, relative_depletion)

        export_file(opofile.stem, wn, inten, relative_depletion, energyPerPhoton)

        if tkplot: ax.plot(wn, relative_depletion, label=label)
        else: 

            
            lineColor = {"color": f"rgb{colors[c]}", "shape":"hv"}
            groupItem = {"legendgroup": f'group{group}'}

            # Normalised Intensity
            defaultStyle={"mode": "lines+markers", "fill": 'tozeroy', "marker": {"size":1}, "line":lineColor}
            _del = "\u0394"
            opofile_lg = f"{opofile.name}({_del}:{round(np.diff(wn).mean(), 1)})"
            dataToSend["average"][opofile.name] = makeDataToSend(wn, inten, opofile_lg, update=defaultStyle)
            dataToSend["average_rel"][opofile.name] = makeDataToSend(wn, relative_depletion, opofile_lg, update=defaultStyle)
            dataToSend["average_per_photon"][opofile.name] = makeDataToSend(wn, energyPerPhoton, opofile_lg, update=defaultStyle)
            ################### Averaged Spectrum END #################################

            base_line = np.genfromtxt(basefile).T
            base_line = np.take(base_line, base_line[0].argsort(), 1)
            dataToSend["base"][f"{opofile.name}_base"] = makeDataToSend(wn_original, counts, label, update={"mode": "lines", "line":lineColor, **groupItem })
            dataToSend["base"][f"{opofile.name}_line"] = makeDataToSend(base_line[0], base_line[1], opofile.name, update={"mode": "lines+markers", "line":blackColor, **groupItem, **nolegend})

            c += 2
            group += 1

            if c >= len(colors): c = 1


    binns, intens = binning(xs, ys, delta)
    energyJ_norm = (np.array(binns) * np.array(intens)) / 1e3

    binns_r, intens_r = binning(xs, ys_r, delta)
    
    # export_file(binns, intens, "averaged")
    
    export_file("averaged", binns, intens, intens_r, energyJ_norm)


    if not tkplot: 


        _del = "\u0394"
        defaultStyle={"mode": "lines+markers", "marker": {"size":1}, "line":{"color": "black", "shape":"hv"}}
        avg_lg = f"averaged({_del}:{round(np.diff(binns).mean(), 1)})"
        dataToSend["average"]["average"] = makeDataToSend(binns, intens, avg_lg, update=defaultStyle)

        dataToSend["average_rel"]["average"] = makeDataToSend(binns_r, intens_r, avg_lg, update=defaultStyle)
        dataToSend["average_per_photon"]["average"] = makeDataToSend(binns, energyJ_norm, avg_lg, update=defaultStyle)

        sendData(dataToSend)

    else:
        ax.plot(binns, intens, "k.-", label=f"Averaged: delta={delta}")
        widget.plot_legend = ax.legend()
        widget.mainloop()
    
if __name__ == "__main__":


    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")
    
    opoplot(args)