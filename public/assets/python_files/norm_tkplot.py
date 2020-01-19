
# Built-In modules
import sys
from pathlib import Path as pt

# FELion tkinter figure module
from FELion_widgets import FELion_Tk

from FELion_definitions import read_dat_file

# Data analysis modules
import numpy as np

def main(felixfiles, location, norm_method, output_filename="averaged"):
    dat_location = location / "EXPORT"
    widget = FELion_Tk(title="Felix Averaged plot", location=location/"OUT")
    
    fig, canvas = widget.Figure()

    if norm_method=="Relative": ylabel = "Relative Depletion (%)"
    else: ylabel = "Norm. Intensity"

    ax = widget.make_figure_layout(title="Felix Averaged plot", xaxis="Wavenumber $cm^{-1}$", yaxis=ylabel, yscale="linear", savename="felix_averaged")
    datfiles = [dat_location/f"{filename.stem}.dat" for filename in felixfiles]
    avgfile = dat_location/f"{output_filename}.dat"

    wn, inten = read_dat_file(avgfile, norm_method)
    
    ax.plot(wn, inten, "k.-", label="Averaged", alpha = 0.7, zorder=100)

    print(f"felix dat files: {datfiles}\nAveraged file: {avgfile}")
    for felixfile, datfile in zip(felixfiles, datfiles):
        wn, inten = read_dat_file(datfile, norm_method)
        ax.plot(wn, inten, ".", label=f"{felixfile.name}")
    widget.plot_legend = ax.legend()
    widget.mainloop()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    filenames = args[0:-1]
    norm_method = args[-1]
    
    filenames = [pt(i) for i in filenames]
    location = filenames[0].parent

    if location.name is "DATA":
        location = location.parent
    
    main(filenames, location, norm_method)