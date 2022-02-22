import numpy as np
from pathlib import Path as pt
from io import StringIO

from FELion_widgets import FELion_Tk
from FELion_definitions import sendData
from FELion_constants import colors

from uncertainties import unumpy as unp
from scipy.optimize import curve_fit
from scipy.special import voigt_profile


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

    removeNanInd = np.isnan(depletion_counts)
    depletion_counts = depletion_counts[np.logical_not(removeNanInd)]
    freq = freq[np.logical_not(removeNanInd)]
    
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

def plot_thz(ax=None, save_dat=True):

    justPlot = args["justPlot"]
    binData = args["binData"]
    delta = args["binSize"]*1e-6 # in kHz
    xs, ys = [], []

    dataToSend = {"resOnOff_Counts":{}, "thz":{}}
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

        if justPlot:

            dataToSend["thz"][f"{filename.name}"] = {"x": list(freq), "y": list(depletion_counts), "name": lg, 
                "mode":'lines+markers',"type": "scattergl", "fill":"tozeroy", "line":{"color":f"rgb{colors[i*2]}", "shape":"hvh"}
            }
            dataToSend["resOnOff_Counts"][f"{filename.name}_On"] = {"x": list(freq), "y": resOnCounts.mean(axis=0).tolist(), "name": f"{filename.name}_On", 
                "mode":'markers',"type": "scattergl", "line":{"color":f"rgb{colors[i*2]}", "shape":"hvh"}
            }

            dataToSend["resOnOff_Counts"][f"{filename.name}_Off"] = {"x": list(freq), "y": resOffCounts.mean(axis=0).tolist(), "name": f"Off: {freq_resOff}GHz: {iteraton}", 
                "mode":'markers',"type": "scattergl", "line":{"color":f"rgb{colors[i*2+1]}", "shape":"hvh"}
            }
            continue


        _, fit_data, params = fitData(freq, depletion_counts)
        uline_freq, uamplitude, *fwhmParameter = params
        
        if voigtFit:
            fG = fwhmParameter[0]*(2*np.sqrt(2*np.log(2)))
            fL = 2*fwhmParameter[1]
            ufwhm = 0.5346 * fL + (0.2166*fL**2 + fG**2)**0.5
            lg_fit = f"{uline_freq*1000:.3fP} [fV:{ufwhm*1000:.3fP} (fG:{fG*1000:.3fP}, fL:{fL*1000:.3fP})] MHz"
        else:
            ufwhm = fwhmParameter[0]*(2*np.sqrt(2*np.log(2))) if gaussianFit else 2*fwhmParameter[0]
            lg_fit = f"{uline_freq*1000:.3fP} [{('fG:', 'fL:')[lorrentFit]}{ufwhm*1000:.3fP}] MHz"

        ms = 7
        if tkplot:
            ax.plot(freq, depletion_counts, f"C{i}.", label=lg, ms=ms)
            ax.plot(freq, fit_data, f"C{i}-", label=lg_fit, zorder=100)
        else:
            dataToSend["thz"][f"{filename.name}"] = {"x": list(freq), "y": list(depletion_counts), "name": lg,
                "mode": 'lines+markers', "type": "scattergl", "fill": "tozeroy", "line": {"color": f"rgb{colors[i*2]}", "shape": "hvh"}
            }
            
            dataToSend["thz"][f"{filename.name}_fit"] = {"x":  list(freq), "y":  list(fit_data), "name":  lg_fit, 
                "mode": 'lines', "type": "scattergl", "line": {"color": f"rgb{colors[i*2]}"}
            }
            
            dataToSend["resOnOff_Counts"][f"{filename.name}_On"] = {"x": list(freq), "y": resOnCounts.tolist()[0], "name": f"{filename.name}_On", 
                "mode":'markers',"type": "scattergl", "line":{"color":f"rgb{colors[i*2]}"}
            }
            
            dataToSend["resOnOff_Counts"][f"{filename.name}_Off"] = {"x": list(freq), "y": resOffCounts.tolist()[0], "name": f"Off: {freq_resOff}GHz: {iteraton}", 
                "mode":'markers', "type": "scattergl","line":{"color":f"rgb{colors[i*2+1]}", }
            }

    if binData or not justPlot: 
        binx, biny = binning(xs, ys, delta)
        export_file(f"binned_{binx.min():.3f}_{binx.max():.3f}GHz_{int(delta*1e6)}kHz", binx, biny)
    
    label = f"Binned (delta={delta*1e6:.2f} KHz)"
    
    if justPlot:
        if binData: 
            dataToSend["thz"]["Averaged_exp"] = { "x": list(binx), "y": list(biny),  
            "name":label, "mode":'lines+markers', "type":"scattergl","fill":"tozeroy", "line":{"color":"black", "shape":"hvh"} }
        return dataToSend

    _, fit_data, params = fitData(binx, biny)
    uline_freq, uamplitude, *fwhmParameter = params

    ufwhm = fwhmParameter[0]*(2*np.sqrt(2*np.log(2))) if gaussianFit else 2*fwhmParameter[0]

    if voigtFit:
        fG = fwhmParameter[0]*(2*np.sqrt(2*np.log(2)))
        fL = 2*fwhmParameter[1]
        ufwhm = 0.5346 * fL + (0.2166*fL**2 + fG**2)**0.5
        lg_fit = f"{uline_freq*1000:.3fP} [fV:{ufwhm*1000:.3fP} (fG:{fG*1000:.3fP}, fL:{fL*1000:.3fP})] MHz"
    else:
        ufwhm = fwhmParameter[0]*(2*np.sqrt(2*np.log(2))) if gaussianFit else 2*fwhmParameter[0]
        lg_fit = f"{uline_freq*1000:.3fP} [{('fG:', 'fL:')[lorrentFit]}{ufwhm*1000:.3fP}] MHz"

    fwhm = ufwhm.nominal_value
    amplitude = uamplitude.nominal_value
    half_max = amplitude/2
    line_freq_fit = uline_freq.nominal_value

    if save_dat:
        saveDir = location / "OUT"
        if not saveDir.exists(): saveDir.mkdir()

        with open(saveDir / "averaged_thz_fit.dat", "w") as f:
            f.write("#Frequency(in MHz)\t#Intensity\n")
            for freq, inten in zip(binx, fit_data): f.write(f"{freq*1e3}\t{inten}\n")

            print(f"averaged_thz_fit.dat file saved in {saveDir}")
    if tkplot:

        ax.plot(binx, biny, "k.", label=label, ms=ms)
        ax.plot(binx, fit_data, "k-", label=lg_fit, zorder=100)
        ax.vlines(x=line_freq_fit, ymin=0, ymax=amplitude, zorder=10)
        ax.hlines(y=half_max, xmin=line_freq_fit-fwhm/2, xmax=line_freq_fit+fwhm/2, zorder=10)
        ax.set(ylim=([-(fit_data.max()/2), fit_data.max()*1.5]))
        return fit_data
    
    else:

        dataToSend["thz"]["Averaged_exp"] = {
            "x": list(binx), "y": list(biny),  "name":label, "mode":'markers', "marker":{"color":"black"}
        }

        dataToSend["thz"]["Averaged_fit"] = {
            "x": list(binx), "y": list(fit_data),  "name": lg_fit, 
            "mode":'line',  "line":{"color":"black"}
        }

        dataToSend["text"] = {
            "x":[line_freq_fit-9e-5, line_freq_fit],
            "y":[half_max*.7, -2],
            "text":[f"{fwhm*1e6:.1f} KHz", f"{line_freq_fit:.7f} GHz"],
            "mode":"text", 
            "showlegend":False

        }

        dataToSend["shapes"] = {
                "center": {
                    "type":"line", "x0":line_freq_fit, "x1":line_freq_fit,
                    "y0": 0, "y1":amplitude,
                },
                "fwhm": {
                    "type":"line", "x0":line_freq_fit-fwhm/2, "x1":line_freq_fit+fwhm/2,
                    "y0": half_max, "y1":half_max

                }
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
        widget = FELion_Tk(title="THz Scan", location=filenames[0].parent)
        widget.Figure()
        if len(filenames) == 1: savename=filenames[0].stem
        else: savename = "averaged_thzScan"
        ax = widget.make_figure_layout(title="THz scan", xaxis="Frequency (GHz)", yaxis="Depletion (%)", savename=savename)
        fit_data = plot_thz(ax=ax)
        widget.plot_legend = ax.legend(title=f"Intensity: {fit_data.max():.2f} %")
        widget.plot_legend.set_draggable(True)
        widget.mainloop()
    else: 
        dataToSend = plot_thz()
        sendData(dataToSend, calling_file=pt(__file__).stem)

def fitData(freq, inten):
    
    global gaussianFit, lorrentFit, voigtFit
    
    # fG and fL are FWHM in MHz 
    fL = float(args["fL"])
    gamma = fL/2
    
    fG = float(args["fG"])
    sigma = fG/(2*np.sqrt(2*np.log(2)))
    
    if fL == 0:
        gaussianFit = True
        fwhmParameter = [sigma]
    
    elif fG == 0:
        lorrentFit = True
        fwhmParameter = [gamma]
    
    elif fG > 0 and fL > 0:
        voigtFit = True
        fwhmParameter = [sigma, gamma]


    def fitProfile(x, x0, A, *args):

        if gaussianFit:
            sig = args
            gam = 0
        elif lorrentFit:
            gam = args
            sig = 0
        elif voigtFit:
            sig, gam = args

        profile = voigt_profile(x-x0, sig, gam)
        norm = profile/profile.max()
        normalisedProfile = A*norm

        return normalisedProfile
    
    freq *= 1000  # GHz --> MHz
    maxIntenInd = inten.argmax()
    amplitude = inten[maxIntenInd]
    cen = freq[maxIntenInd]

    p0=[cen, amplitude, *fwhmParameter]
    pop, pcov = curve_fit(fitProfile, freq, inten, p0=p0)
    perr = np.sqrt(np.diag(pcov))
    print(f"{pop=}\n{perr=}", flush=True)

    fittedY = fitProfile(freq, *pop)

    # MHz --> GHz
    freq /= 1000 

    pop[0] /= 1000
    perr[0] /= 1000
    
    pop[2] /= 1000
    perr[2] /= 1000
    
    if voigtFit:
        pop[3] /= 1000
        perr[3] /= 1000
    params = unp.uarray(pop, perr)
    return freq, fittedY, params


args = None
widget = None

voigtFit = False
lorrentFit = False
gaussianFit = False
tkplot, filenames, location = None, None, None


def main(arguments):
    global args, tkplot, filenames, location

    args = arguments
    tkplot = args["tkplot"]
    filenames = [pt(i) for i in args["thzfiles"]]
    location = pt(filenames[0].parent)

    thz_function()
