
import json
import sys
from pathlib import Path as pt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from felix_tkplot_definitions import felix_plot, theoryplot, Marker
from FELion_widgets import FELion_Tk

import matplotlib.gridspec as gridspec
marker_theory = None

def plotGraph(plotArgs):

    global marker_theory

    figwidth, figheight, dpi, freqScale, gridalpha, theorysigma, majorTick = plotArgs["numberWidgets"]

    NPlots = 1

    ratio = "1"
    
    figcaption, figtitle, exptitle, legend_labels, calcTitle, marker = plotArgs["textWidgets"]
    print(plotArgs["textWidgets"], type(plotArgs["textWidgets"]), figcaption, figtitle, exptitle, legend_labels, calcTitle, marker)

    normMethod = plotArgs["normMethod"]
    
    sameColor, invert_ax2, onlyExp, hide_axis, hide_all_axis, legend_visible = plotArgs["booleanWidgets"]
    hspace = 0.05
    wspace = 0.05

    datlocation = pt(plotArgs["location"]) / "../EXPORT"
    print(plotArgs["selectedWidgets"], flush=True)
    datfiles, fundamentalsfiles, overtonefiles, combinationfiles = plotArgs["selectedWidgets"]
    datfiles = [datlocation/i for i in datfiles]
    
    grid_ratio = np.array(ratio.split(","), dtype=float)
    grid = {"hspace": hspace, "wspace": wspace, "width_ratios": grid_ratio}
    
    nrows = (2, 1)[onlyExp]
    figheight = (figheight, figheight/2)[onlyExp]
    


    widget = FELion_Tk(title="Felix Averaged plot", location=datlocation/"../OUT")
    
    fig, canvas = widget.Figure(dpi=dpi, default_widget=False, default_save_widget=True, connect=False, executeCodeWidget=False)
    

    axs = []
    gs = gridspec.GridSpec(nrows, NPlots, figure=fig)

    for _i in gs:
        temp = fig.add_subplot(_i)
        axs.append(temp)

    # print(axs)

    lg = [i.strip() for i in legend_labels.split(",")]

    
    if onlyExp:
        only_exp_plot(axs, datfiles, NPlots, exptitle, lg, normMethod, majorTick, legend_visible, hide_all_axis, legend_labels, sameColor)

        widget.mainloop()
        return

    theoryLocation = pt(plotArgs["theoryLocation"])
    theoryfiles = [pt(theoryLocation)/i for i in fundamentalsfiles]
    overtonefiles = [pt(theoryLocation)/i for i in overtonefiles]
    combinationfiles = [pt(theoryLocation)/i for i in combinationfiles]

    theoryfiles1_overt_comb = []
    theoryfiles2_overt_comb = []
    
    if len(combinationfiles) + len(overtonefiles) > 0: 

        theoryfiles1_overt_comb = np.append(overtonefiles[0], combinationfiles[0])

    if len(combinationfiles) + len(overtonefiles) > 1: 
        theoryfiles2_overt_comb = np.append(overtonefiles[1], combinationfiles[1])

    theory_color = (len(datfiles), 1)[sameColor]
    for i in range(NPlots):
        
        if NPlots > 1: 
            ax_exp = axs[0, i]
            ax_theory = axs[1, i]
        else:
            ax_exp = axs[i]
            ax_theory = axs[i+1]
        
        ax_exp = felix_plot(datfiles, ax_exp, lg, normMethod, sameColor)
        
        linestyle = ["--", ":"]
        
        for tColorIndex, theoryfile in enumerate(theoryfiles):
            ax_theory = theoryplot(theoryfile, ax_theory, freqScale, theory_color+tColorIndex, theorysigma)
        for tfile1, ls in zip(theoryfiles1_overt_comb, linestyle):
            ax_theory = theoryplot(tfile1, ax_theory, freqScale, f"{theory_color}{ls}", theorysigma)
        for tfile2, ls in zip(theoryfiles2_overt_comb, linestyle):
            ax_theory = theoryplot(tfile2, ax_theory, freqScale, f"{theory_color+1}{ls}", theorysigma)
        
        if invert_ax2: ax_theory.invert_yaxis()
        
        #ax_theory.minorticks_on()
        
        # ax_exp
        if hide_axis:
            ax_theory.spines["top"].set_visible(False)
            ax_exp.spines["bottom"].set_visible(False)
            
        ax_exp.tick_params(labelbottom=False, bottom=False, labeltop=True, top=True) # removing x-ticks label
        
        #ax_exp.minorticks_on()

        ax_exp.xaxis.set_tick_params(which='minor', bottom=False, top=True)
        
        ax_exp.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax_exp.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax_exp.xaxis.set_major_locator(MultipleLocator(majorTick))
        
        ax_theory.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax_theory.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax_theory.xaxis.set_major_locator(MultipleLocator(majorTick))
        
        ax_theory.get_shared_x_axes().join(ax_theory, ax_exp)
        
        # Labels
        if i<1:
            
            ylabel="Norm. Intensity ~(m$^2$/photon)"
            
            ax_exp.set_ylabel((ylabel, "Relative Depletion (%)")[normMethod=="Relative"], fontsize=12)
            ax_theory.set_ylabel("Intensity (km/mol)", fontsize=12)

            if legend_visible:
                if legend_labels == "": ax_exp.legend([], title=exptitle.strip()).set_draggable(True)
            
                else: ax_exp.legend(title=exptitle.strip()).set_draggable(True)
                ax_theory.legend(title=calcTitle.strip()).set_draggable(True)
            marker_theory = Marker(fig, canvas, ax_theory, ax_exp, txt_value=marker.split(","))
            
        elif i==NPlots-1:
            ax_exp.yaxis.tick_right()
            ax_theory.yaxis.tick_right()
        else:
            ax_exp.tick_params(labelbottom=False, bottom=False, labelleft=False, left=False, labeltop=True, top=True)
            ax_exp.yaxis.set_tick_params(which='minor', left=False, right=False, top=True)
            
            ax_theory.tick_params(labelleft=False, left=False)
            ax_theory.yaxis.set_tick_params(which='minor', left=False)
        
        
        
    # Figure caption

    fig.text(0.5, 0.09, "Wavenumber (cm$^{-1}$)", wrap=True, horizontalalignment='center', fontsize=12)
    fig.text(0.5, 0.01, figcaption, wrap=True, horizontalalignment='center', fontsize=12)
    canvas.draw()
    
    widget.mainloop()

def only_exp_plot(axs, datfiles, NPlots, exptitle, lg, normMethod, majorTick, legend_visible, hide_all_axis, legend_labels, sameColor):


    for i in range(NPlots):
    
        ax = axs[i]

        ax = felix_plot(datfiles, ax, lg, normMethod, sameColor)
    
        ax.xaxis.set_tick_params(which='minor', bottom=True)

        ax.xaxis.set_minor_locator(AutoMinorLocator(5))
        ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        ax.xaxis.set_major_locator(MultipleLocator(majorTick))

        ylabel="Norm. Intensity ~($m^2/photon$)"
        ax.set_ylabel((ylabel, "Relative Depletion (%)")[normMethod=="Relative"], fontsize=12)

        ax.set_xlabel("Wavenumber ($cm^{-1}$)", fontsize=12)

        if legend_visible and i<2:

            if legend_labels == "": ax.legend([], title=exptitle.strip).set_draggable(True)

            else: ax.legend(title=exptitle.strip()).set_draggable(True)


        if hide_all_axis:
            ax.spines["top"].set_visible(False)
            ax.spines["bottom"].set_visible(False)
            ax.spines["left"].set_visible(False)
            ax.spines["right"].set_visible(False)

            ax.xaxis.set_tick_params(which='minor', bottom=False)
            ax.yaxis.set_tick_params(which='minor', left=False)

            ax.tick_params(labelbottom=False, bottom=False, labelleft=False, left=False)

            ax.set(xlabel="", ylabel="")

    return ax

def main(args):
    plotGraph(args)