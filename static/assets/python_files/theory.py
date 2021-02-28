
# Importing Built-In modules
import json, sys
from pathlib import Path as pt

# FELion Modules
from FELion_widgets import FELion_Tk
from FELion_definitions import read_dat_file
from FELion_definitions import sendData

# Data analysis
import numpy as np

def gaussian(x, A, sig, center): return A*np.exp(-0.5*((x-center)/sig)**2)

def generateNGaussian(N):

    gaussfn = lambda n: f"A{n}*(np.exp((-1.0/2.0)*(((x-cen{n})/sigma{n})**2)))+"
    _gfn, _args = "", "x, "
    for i in range(int(N)): 
        _gfn += gaussfn(i)
        _args += f"cen{i}, A{i}, sigma{i}, "
    exec(f"gfn_ = lambda {_args.strip()[:-1]}: {_gfn.strip()[:-1]}")
    
    return locals()["gfn_"]

def computeNGaussian(wn, inten, sigma=5):

    _args = {}
    N = len(wn)
    print(N)
    gfn = generateNGaussian(N)
    i = 0
    for x, y in zip(wn, inten):
        _args[f"cen{i}"] = x
        _args[f"A{i}"] = y
        _args[f"sigma{i}"] = sigma
        i += 1
    full_wn = np.linspace(wn.min()-100, wn.max()+100, 5000)

    full_inten = gfn(full_wn, **_args)
    return full_wn, full_inten


def exp_theory(args, output_filename="averaged"):

    theoryfiles = [pt(i) for i in args["theoryfiles"]]
    normMethod = args["normMethod"]
    sigma = args["sigma"]
    
    scale = args["scale"]
    currentLocation = pt(args["currentLocation"])
    tkplot = args["tkplot"]

    onlyExpRange = args["onlyExpRange"]
    
    if tkplot:
        
        widget = FELion_Tk(title="Exp. Vs Theory", location=theoryfiles[0].parent)
        fig, canvas = widget.Figure()
        if len(theoryfiles) == 1: savename=theoryfiles[0].stem
        else: savename = "Exp vs Theory"
        
        if normMethod == "Relative": ylabel = "Relative Depletion (%)"
        
        else: ylabel =  "Norm. Intensity"
        ax = widget.make_figure_layout(title="Experimental vs Theory", xaxis="Wavenumber $(cm^{-1})$", yaxis=ylabel, yscale="linear", savename=savename)

    print(currentLocation)
    if currentLocation.name == "DATA": datfile_location = currentLocation.parent/"EXPORT"
    else: datfile_location = currentLocation/"EXPORT"

    avgfile = datfile_location/f"{output_filename}.dat"
    print(avgfile)

    xs, ys = read_dat_file(avgfile, normMethod)

    if tkplot: ax.plot(xs, ys, "k-", label="Experiment", alpha=0.9)
    else:

        data = {"line_simulation":{}, "averaged": {
                    "x": list(xs), "y": list(ys),  "name": "Exp",
                    "mode": "lines", "marker": {"color": "black"},
            }}


    for theoryfile in theoryfiles:

        x, y = np.genfromtxt(theoryfile).T[:2]
        x = x*scale

        if onlyExpRange: 
            new_x = x[x<=xs.max()]

            new_x = new_x[new_x>=xs.min()]
            if len(new_x) > 0: 
                start_ind, = np.where(x==new_x[0])[0]
                x = new_x
            else: start_ind = 0
        else: start_ind = 0


        y = y[start_ind:len(x)+start_ind]
        norm_factor = ys.max()/y.max()
        y = norm_factor*y
        
        theory_x, theory_y = computeNGaussian(x, y, sigma)

        if tkplot: ax.fill(theory_x, theory_y, label=theoryfile.stem)

        else:
            data["line_simulation"][f"{theoryfile.name}"] = {
                    "x":list(theory_x), "y":list(theory_y),  "name":f"{theoryfile.stem}", "fill":"tozerox"
                }


    if not tkplot: sendData(data)
    else:
        widget.plot_legend = ax.legend()
        widget.mainloop()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))

    print(f"Received args: {args}, {type(args)}\n")
    
    exp_theory(args)