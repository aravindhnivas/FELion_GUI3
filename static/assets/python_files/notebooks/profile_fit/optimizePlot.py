
import matplotlib.ticker as plticker

def optimizePlot(ax, xlabel, ylabel, yscale="linear", fmtString="{x:.1f}", Nlocator=5):
    ax.set(yscale="linear")
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)

    ax.minorticks_on()
    ax.tick_params(axis='both', labelsize=16)
    ax.tick_params(which='major', width=2)
    
    
    ax.tick_params(which='minor', width=1)
    ax.tick_params(which='major', length=7)
    ax.tick_params(which='minor', length=4)
    
    ax.xaxis.set_major_formatter(plticker.StrMethodFormatter(fmtString))
    
    
    loc = plticker.MaxNLocator(Nlocator)
    ax.xaxis.set_major_locator(loc)
    return ax