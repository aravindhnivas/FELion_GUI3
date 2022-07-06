from pathlib import Path as pt
import numpy as np
from felionlib.utils.felionQt import felionQtWindow
from uncertainties import ufloat_fromstr

def readTHz_fitfile(fitfile: pt):
    with open(fitfile, 'r') as f:
        contents = f.readlines()
    freq = None
    amp = None
    fwhm = None
    fitMethod = None
    
    for line in contents:
        if not line.startswith('#'):
            break
        
        if 'freq = ' in line:
            freq = ufloat_fromstr(line.split('=')[1].strip())
        
        if 'amp = ' in line:
            amp = ufloat_fromstr(line.split('=')[1].strip())
        
        if 'fwhm = ' in line:
            fwhm = ufloat_fromstr(line.split('=')[1].strip())
        
        if 'fitMethod = ' in line:
            fitMethod = line.split('=')[1].strip()
    
    return freq, amp, fwhm, fitMethod

def main(args):

    location = pt(args["location"])
    thzfiles: list[pt] = [location / file for file in args["thzfiles"]]
    includeFit = args["includeFit"]

    widget = felionQtWindow(
        title=f"THz spectrum",
        figXlabel="Frequency [GHz]",
        figYlabel="Depletion [%]",
        ticks_direction="out",
        location=location / "OUT",
        savefilename="thzspec",
    )

    legend_handler = {}
    zorder_max = len(thzfiles) + 1
    
    unit = None
    
    for index, thzfile in enumerate(thzfiles):
        
        freq, depletion = np.genfromtxt(thzfile).T
        color = f"C{index}"
        alpha = 1
        # zorder = None
        
        if len(thzfiles) > 1:
            if 'bin.thz' in thzfile.name:
                color = 'k'
            else:
                alpha = 0.5
                    
        
        with open(thzfile, 'r') as f:
            
            contents = f.readlines()
            
            label = contents[0].split('#')[1].strip()
            unit = contents[1].split('#')[1].strip()
            fitfile = thzfile.parent / thzfile.name.replace('.dat', ".fit.dat")
            fit_label = label + " (fit)"
            
            if includeFit and fitfile.exists():
                freq_fit, depletion_fit = np.genfromtxt(fitfile).T
                legend_handler[label] = widget.ax.fill_between(
                    freq, depletion, label=label, 
                    alpha=0.5, color=color, ec="none", step="pre"
                )
                (legend_handler[fit_label],) = widget.ax.plot(
                    freq_fit, depletion_fit, label=fit_label, color=color, alpha=alpha
                )
                
                if 'bin.thz' in thzfile.name:
                    legend_handler[fit_label].set_zorder(zorder_max)
                    
            else:
                (legend_handler[label],) = widget.ax.plot(
                    freq, depletion, label=label, color=color, alpha=alpha
                )
                if 'bin.thz' in thzfile.name:
                    legend_handler[label].set_zorder(zorder_max)
                    
    if unit:
        widget.ax.set_xlabel(unit)
        
    widget.makeLegendToggler(legend_handler, edit_legend=True)
    widget.optimize_figure(setBound=False)
    widget.fig.tight_layout()
    widget.qapp.exec()
    