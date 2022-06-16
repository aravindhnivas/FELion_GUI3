from matplotlib.axes import Axes
import numpy as np
from pathlib import Path as pt
from io import StringIO
from felionlib.utils.FELion_definitions import sendData
from felionlib.utils.FELion_constants import colors
from felionlib.utils.fit_profile.lineProfileFit import fitData
from felionlib.utils.felionQt import felionQtWindow
import matplotlib.ticker as plticker


def thz_plot(filename):

    with open(filename, "r") as fileContents:
        file = fileContents.readlines()

    startInd = 1
    if "=" in file[0]:
        iteraton = int(file[0].split("=")[-1])
        startInd = 2
    else:
        iteraton = int(file[0].split("\n")[0].split("\t")[-1])
    print(f"{iteraton=}", flush=True)
    
    # Getting rid of the first line
    file = file[startInd:]

    currentInd = 0
    for line in file:
        if line.startswith("#"): break
        line = line.split("\n")[0].split("\t")[:-1]
        currentInd += 1

    resONDataContents = "".join(file[:currentInd])
    resOn = np.genfromtxt(StringIO(resONDataContents))[1:]
    
    resOFFDataContents = "".join(file[currentInd:2*(currentInd+1)])
    resOff = np.genfromtxt(StringIO(resOFFDataContents))[1:]

    freq = resOn.T[0]
    freq_resOff = resOff.T[0][0]

    resOnCounts = resOn.T[1:iteraton+1]
    resOffCounts = resOff.T[1:iteraton+1]
    
    depletion = (resOffCounts - resOnCounts)/resOffCounts
    depletion_counts = depletion.T.mean(axis=1)

    depletion_counts = depletion_counts*100
    steps = int(round((freq[1]-freq[0])*1e6, 0))
    
    finiteInd = np.isfinite(depletion_counts)
    depletion_counts = depletion_counts[finiteInd]
    freq = freq[finiteInd]
    # print(f"{depletion_counts=}", flush=True)
    return freq, depletion_counts, steps, iteraton, resOffCounts, resOnCounts, freq_resOff

def binning(xs, ys, delta=1e-5):

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
    # print("after binning", binsx, data_binned)
    binsx = np.array(binsx, dtype=float)

    data_binned = np.array(data_binned, dtype=float)
    return binsx, data_binned

def plot_thz(widget: felionQtWindow=None, save_dat=True, tkplot=False):

    justPlot = args["justPlot"]
    binData = args["binData"]
    delta = args["binSize"]*1e-6 # in kHz
    
    xs, ys = [], []
    line_handler = {}
    
    dataToSend = {"resOnOff_Counts": {}, "thz": {"individual": {}, "averaged": {}}}
    c =  0

    for i, filename in enumerate(filenames):

        filename = pt(filename)
        freq, depletion_counts, steps, iteraton, resOffCounts, resOnCounts, freq_resOff = thz_plot(filename)
        
        xs = np.append(xs, freq)
        ys = np.append(ys, depletion_counts)
        
        export_file(filename.stem, freq, depletion_counts)
        if i >= int(len(colors)/2):
            i = c
            c += 1
        lg = f"{filename.name} [{steps} KHz : {iteraton} cycles]"

        # if tkplot:
        #     (line_handler[lg], ) = widget.ax.plot(freq, depletion_counts, label=lg)
        
        dataToSend["thz"]["individual"][f"{filename.name}"] = {
            "x": list(freq), "y": list(depletion_counts), "name": lg, 
            "mode":'lines+markers',"type": "scattergl", "fill":"tozeroy", "line":{"color":f"rgb{colors[i*2]}", "shape":"hvh"}
        }
        dataToSend["resOnOff_Counts"][f"{filename.name}_On"] = {
            "x": list(freq), "y": resOnCounts.mean(axis=0).tolist(), "name": f"{filename.name}_On", 
            "mode": 'markers',"type": "scattergl", "line": {"color": f"rgb{colors[i*2]}", "shape":"hvh"}
        }

        dataToSend["resOnOff_Counts"][f"{filename.name}_Off"] = {
            "x": list(freq), "y": resOffCounts.mean(axis=0).tolist(), 
            "name": f"Off: {freq_resOff}GHz: {iteraton}", "mode": 'markers', "type": "scattergl",
            "line": {"color": f"rgb{colors[i*2+1]}", "shape": "hvh"}
        }
        print(f"Current: {fitfile=}\n{filename.name=}\n", flush=True)

        
        if filename.name != fitfile or justPlot or tkplot: 
            continue

        
        if len(plotIndex)>0:
            
            ind = np.logical_and(freq>=plotIndex[0], freq<=plotIndex[-1])
            freq = freq[ind]
            depletion_counts = depletion_counts[ind]
            
        fittedParamsTable, fittedInfos = fitData(
            freq, depletion_counts, varyAll=varyAll,
            method=fitMethod, paramsTable=paramsTable, fitfile=fitfile
        )
        
        fittedY = fittedInfos["fittedY"]
        dataToSend["fittedParamsTable"] = fittedParamsTable
        dataToSend["fittedInfos"] = {"freq": fittedInfos["freq"].tolist(), "fittedY": fittedInfos["fittedY"].tolist()}
        
        dataToSend["thz"]["individual"][f"{filename.name}_fit"] = {
            "x": list(freq), "y": list(fittedY), "name": fitMethod, 
            "mode": 'lines', "type": "scattergl", "line": {"color": f"rgb{colors[i*2]}"}
        }


    # if tkplot:
    #     widget.makeLegendToggler(line_handler)
        
    if not binData:
        return dataToSend

    binx, biny = binning(xs, ys, delta)
    export_file(f"binned_{binx.min():.3f}_{binx.max():.3f}GHz_{int(delta*1e6)}kHz", binx, biny)
    

    binDatalabel = f"Binned (delta={delta*1e6:.2f} KHz)"
    if tkplot:
        (line_handler[binDatalabel],) = widget.ax.plot(binx, biny, "k", label=binDatalabel)
        widget.makeLegendToggler(line_handler)
        return
    
    dataToSend["thz"]["averaged"]["averaged"] = {
        "x": list(binx), "y": list(biny), "name": binDatalabel, 
        "mode": 'lines+markers', "type": "scattergl","fill": "tozeroy",
        "line": {"color": "black", "shape": "hvh"}
    }
    
    if not fitfile == "averaged" or justPlot or tkplot:
        return dataToSend
    
    if len(plotIndex)>0:

        ind = np.logical_and(binx>=plotIndex[0], binx<=plotIndex[-1])
        binx = binx[ind]
        biny = biny[ind]
    
    fittedParamsTable, fittedInfos = fitData(
        binx, biny, varyAll=varyAll, fitfile=fitfile,
        method=fitMethod, paramsTable=paramsTable
    )
    fittedY = fittedInfos["fittedY"]
    dataToSend["fittedParamsTable"] = fittedParamsTable
    dataToSend["fittedInfos"] = {"freq": fittedInfos["freq"].tolist(), "fittedY": fittedInfos["fittedY"].tolist()}

    if save_dat:
        saveDir = location / "OUT"
        if not saveDir.exists(): saveDir.mkdir()
        with open(saveDir / "averaged_thz_fit.dat", "w") as f:
            f.write("#Frequency(in MHz)\t#Intensity\n")
            for freq, inten in zip(binx, fittedY): f.write(f"{freq*1e3}\t{inten}\n")
            print(f"averaged_thz_fit.dat file saved in {saveDir}")

    
    dataToSend["thz"]["averaged"]["averaged_fit"] = {
        "x": list(binx), "y": list(fittedY), "name": fitMethod, 
        "mode": 'line',  "line": {"color": "black"}
    }

    return dataToSend

      
def export_file(fname, freq, inten):

        freq = np.array(freq, dtype=float)
        inten = np.array(inten, dtype=float)
        EXPORT_DIR = location / "EXPORT"
        if not EXPORT_DIR.exists(): 
            EXPORT_DIR.mkdir()

        if args["saveInMHz"]: 
            unit = "MHz"
            freq *= 1000
        else:
            unit = "GHz"

        with open(EXPORT_DIR/f"{fname}.dat", 'w+') as f:
            f.write(f"#Frequency({unit})\t#DepletionCounts(%)\n")
            for i in range(len(freq)): f.write(f"{freq[i]}\t{inten[i]}\n")

def thz_function():

    global widget
    if tkplot:
        if len(filenames) == 1: 
            savefilename=filenames[0].stem
            
        else:
            savefilename = "averaged_thzScan"
        
        widget = felionQtWindow(title=savefilename,
            figXlabel="Frequency (GHz)", figYlabel="Counts",
            location=location/"OUT", savefilename=savefilename
        )
        
        plot_thz(widget, tkplot=True)
        
        widget.ax.xaxis.set_major_formatter(plticker.StrMethodFormatter("{x:.3f}"))
        
        widget.optimize_figure()
        widget.fig.tight_layout()
        widget.qapp.exec()

    else: 
        dataToSend = plot_thz()
        sendData(dataToSend, calling_file=pt(__file__).stem)


args = None
widget: felionQtWindow = None
fitfile = None
fitMethod = "lorentz"
paramsTable = []
varyAll = False
tkplot, filenames, location = None, None, None

plotIndex = []


def main(arguments):

    global args, tkplot, filenames, location,\
        fitfile, fitMethod, paramsTable, varyAll, plotIndex
    
    args = arguments
    tkplot = args["tkplot"]
    filenames = [pt(i) for i in args["thzfiles"]]

    location = pt(filenames[0].parent)
    fitfile = args["fitfile"]
    fitMethod = args["fitMethod"]
    paramsTable = args["paramsTable"]
    varyAll = args["varyAll"]
    plotIndex = args["plotIndex"]
    
    thz_function()
    