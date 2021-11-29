# Built-In modules
import sys, json
from pathlib import Path as pt

# FELion tkinter figure module
from FELion_widgets import FELion_Tk
from FELion_definitions import read_dat_file

# Data analysis modules
import numpy as np

# def theory_plot(theoryfiles, ax, freqScale=1, color=1, theorysigma=5):
    
#     for theoryfile in theoryfiles:
        
#         try:
#             # Getting legend info from theoryfile
#             with open(theoryfile, "r") as f:
#                 readfile = f.readlines()
#             legendName = readfile[1].split(" ")[-1].split("\n")[0]
#         except: legendName = ""

#         # Reading theoryfile
#         freq_t, inten_t = np.genfromtxt(theoryfile).T[:2]

#         # Frequnecy scaling
#         freq_t *= freqScale

#         # theory plotting
#         freq_tsim, inten_tsim = computeNGaussian(freq_t, inten_t, theorysigma)
#         theory_lines = ax.plot(freq_tsim, inten_tsim, f"C{color}", label=legendName)
#         color += 1
        
#     return ax

def felix_plot(filename, ax, lg, normMethod="IntensityPerPhoton", color=0, sameColor=True):
    
    for i, f in enumerate(filename):
        
        if not sameColor: color += i
            
        if normMethod == "addedFile":
            data = np.genfromtxt(f).T
            wn = data[0]
            inten = data[2]*1e3
            ax.fill_between(wn, inten, color=f"C{color}", step="pre", alpha=0.4)
        else:
            freq_exp, inten_exp = read_dat_file(f, normMethod)
            ax.fill_between(freq_exp, inten_exp, color=f"C{color}",step="pre", alpha=0.4)
            
        fullfit_file = f.parent / f"{f.stem}_{normMethod}.fullfit"
        freq_sim, inten_sim = np.genfromtxt(fullfit_file).T
        try:
            ax.plot(freq_sim, inten_sim, f"C{color}", zorder=2, label=lg[i])
        except:
            ax.plot(freq_sim, inten_sim, f"C{color}", zorder=2)
        
    return ax

def fitted_vlines(ax, filename, loc, normMethod, color):
    filename = (f"{filename.stem}_Log.expfit", f"{filename.stem}_addedFile.expfit")[normMethod=="addedFile"]

    expfit = loc / filename

    data = np.genfromtxt(expfit).T
    y0, y1 = ax.get_ylim()
    
    args = dict(color=f"C{color}", alpha=0.5, ls="--")
    if type(data[0]) is np.ndarray:
        for f in data[0]: 
            ax.vlines(f, y0, y1 , **args)
    else: 
        ax.vlines(data[0], y0, y1, **args)

    return ax

def mainplot(args):

    location = pt(args["location"])
    normMethod = args["normMethod"]
    output_filename = "averaged"

    # dat_location = location / "../EXPORT"
    avgfile = location/f"../EXPORT/{output_filename}.dat"

    widget = FELion_Tk(title="Felix Averaged plot", location=location/"../OUT")
    fig, canvas = widget.Figure()

    if normMethod=="Relative": ylabel = "Relative Depletion (%)"
    else: ylabel = "Norm. Intensity"

    ax = widget.make_figure_layout(title="Felix Averaged plot", xaxis="Wavenumber $cm^{-1}$", yaxis=ylabel, yscale="linear", savename="felix_averaged")
    
    
    lg=["Averaged"]
    ax = felix_plot([avgfile], ax, lg, normMethod)
    # plt.show()
    widget.plot_legend = ax.legend()

    widget.mainloop()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")
    mainplot(args)

    # print("Argument received for normline_tkplot.py: \n", sys.argv[1:][0])
    # args = sys.argv[1:][0].split(",")    
    # print("Argument procesed:\n", args)
    # filenames = args[0:-2]
    
    # normMethod = args[-2]
    
    # # onlyFinalSpectrum = (False, True)[args[-1] == "true"]

    # filenames = [pt(i) for i in filenames]

    # location = filenames[0].parent

    # if location.name == "DATA": location = location.parent

    # main(filenames, location, normMethod)