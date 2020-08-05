
import json, sys
from pathlib import Path as pt
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, MultipleLocator
from felix_tkplot_definitions import felix_plot, theoryplot, Marker

marker_theory = None


def plotGraph(plotArgs):

    figwidth, figheight, dpi, freqScale, gridalpha, theorysigma, majorTick = [i["value"] for i in plotArgs["number"]]
    
    NPlots = 1

    ratio = "1"
    

    
    figcaption, figtitle, exptitle, legend_labels, calcTitle, marker =  [i["value"] for i in plotArgs["text"]]
    normMethod = "Log"
    
    sameColor, invert_ax2, onlyExp, hide_all_axis, hide_axis, legend_visible = [i["value"] for i in plotArgs["boolean"]]
   
    hspace = 0.05
    wspace = 0.05


    datlocation = plotArgs["datlocation"]
    datfiles, fundamentalsfiles, overtonefiles, combinationfiles = [i["selected"] for i in plotArgs["checkBoxes"]]
    datfiles = [pt(datlocation)/i for i in datfiles]
    print(datfiles)

    global marker_theory
    
    # plt.close()
    
    grid_ratio = np.array(ratio.split(","), dtype=np.float)
    grid = {"hspace": hspace, "wspace": wspace, "width_ratios": grid_ratio, "bottom":0.2}
    
    rows = (2, 1)[onlyExp]
    figheight = (figheight, figheight/2)[onlyExp]
    
    fig, axs = plt.subplots(rows, NPlots, figsize=(figwidth, figheight), dpi=dpi, gridspec_kw=grid)
    lg = [i.strip() for i in legend_labels.split(",")]
    
    
    if onlyExp: 
        ax = only_exp_plot(axs, datfiles, NPlots, exptitle, lg, normMethod, majorTick, legend_visible, hide_all_axis, legend_labels)
        plt.show()

        return 
    theorylocation = pt(plotArgs["theorylocation"])
    fundamentalsfiles = [pt(theorylocation)/i for i in plotArgs["fundamentalsfiles"]]
    overtonefiles = [pt(theorylocation)/i for i in plotArgs["overtonefiles"]]
    combinationfiles = [pt(theorylocation)/i for i in plotArgs["combinationfiles"]]
    # theoryfiles = [pt(theory_loc)/i for i in plotArgs["theoryfiles"]]
    # theoryfiles1_overt_comb = [pt(theory_loc)/i for i in felix_w2.files.value]
    # theoryfiles2_overt_comb = [pt(theory_loc)/i for i in felix_w3.files.value]
   
    theory_color = (len(datfiles), 1)[sameColor]
    
    for i in range(NPlots):
        
        if NPlots > 1: 
            ax_exp = axs[0, i]
            ax_theory = axs[1, i]
        else:
            ax_exp = axs[i]
            ax_theory = axs[i+1]
            
        
        ax_exp = felix_plot(datfiles, ax_exp, lg, normMethod)
        
        linestyle = ["--", ":"]
        
        ax_theory = theoryplot(theoryfiles[0], ax_theory, freqScale, theory_color, theorysigma)
        for tfile1, ls in zip(theoryfiles1_overt_comb, linestyle ):
            ax_theory = theoryplot(tfile1, ax_theory, freqScale, f"{theory_color}{ls}", theorysigma)
        
        #theory_color += 1
        ax_theory = theoryplot(theoryfiles[1], ax_theory, freqScale, theory_color+1, theorysigma)
        for tfile2, ls in zip(theoryfiles2_overt_comb, linestyle):
            ax_theory = theoryplot(tfile2, ax_theory, freqScale, f"{theory_color+1}{ls}", theorysigma)
        
        # ax_theory
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
            
            ylabel="Norm. Intensity ~($m^2/photon$)"
            ax_exp.set_ylabel((ylabel, "Relative Depletion (%)")[normMethod=="Relative"], fontsize=12)
            
            if legend_visible:
                if legend_labels == "": ax_exp.legend([], title=exptitle.strip()).set_draggable(True)
                else: ax_exp.legend(title=exptitle.strip()).set_draggable(True)

                ax_theory.set_ylabel("Intensity (Km/mol)", fontsize=12)
                ax_theory.legend(title=calcTitle.strip()).set_draggable(True)
                
            #marker_exp = Marker(fig, ax_exp)
            marker_theory = Marker(fig, ax_theory, ax_exp, txt_value=marker.split(","))
            
        elif i==NPlots-1:
            ax_exp.yaxis.tick_right()
            ax_theory.yaxis.tick_right()
        else:
            ax_exp.tick_params(labelbottom=False, bottom=False, labelleft=False, left=False, labeltop=True, top=True)
            ax_exp.yaxis.set_tick_params(which='minor', left=False, right=False, top=True)
            
            ax_theory.tick_params(labelleft=False, left=False)
            ax_theory.yaxis.set_tick_params(which='minor', left=False)
        
        
        
    # Figure caption
    plt.figtext(0.5, 0.04, "Wavenumber ($cm^{-1}$)", wrap=True, horizontalalignment='center', fontsize=12)
    plt.figtext(0.5, 0.01, figcaption, wrap=True, horizontalalignment='center', fontsize=12)
    plt.show()


def only_exp_plot(axs, datfiles, NPlots, exptitle, lg, normMethod, majorTick, legend_visible, hide_all_axis, legend_labels):
    for i in range(NPlots):
        if NPlots>1:
            ax = axs[i]
        else:
            ax = axs

        ax = felix_plot(datfiles, ax, lg, normMethod)
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


if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n")
    felix = plotGraph(args)