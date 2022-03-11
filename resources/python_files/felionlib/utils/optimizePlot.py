
import matplotlib.ticker as plticker

def optimizePlot(ax, xlabel, ylabel, title="", yscale="linear", fmt=False, fmtString="{x:.1f}", Nlocator=5):

    ax.set(yscale=yscale)
    
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=16)
    ax.set_ylabel(ylabel, fontsize=16)

    ax.minorticks_on()

    ax.tick_params(which='major', width=2, length=7, labelsize=16)
    ax.tick_params(which='minor', width=1, length=4)
    
    if fmt:
        ax.xaxis.set_major_formatter(plticker.StrMethodFormatter(fmtString))
        loc = plticker.MaxNLocator(Nlocator)
        ax.xaxis.set_major_locator(loc)

    return ax
