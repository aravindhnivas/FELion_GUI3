# Built-in
import os, json, sys
from pathlib import Path as pt

# DATA Analysis
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import c, k, h
from uncertainties import ufloat as uf

# FELion modules
from FELion_widgets import FELion_Tk

from FELion_definitions import sendData

Term = lambda term, order, J: term*((J*(J+1))**order)

energyJ = lambda j, B, D=0, H=0: (Term(B, 1, j)-Term(D, 2, j)+Term(H, 3, j)) *1e6 * h

gJ = lambda j: 2*j + 1

def calculate_population(B, D=0, H=0, temp=5, totalJ=20, tkplot=False, location=None):

    intenJ = lambda j: gJ(j) * np.exp(-energyJ(j, B, D, H)/(k*temp))
    pJ = lambda j, Z: (intenJ(j)/Z)*100

    totalJ = np.arange(totalJ)

    Z = np.array([intenJ(j) for j in totalJ], dtype=float).sum()
    distribution = np.array([pJ(j, Z) for j in totalJ])

    maxIntenJ = np.argmax(distribution)
    
    lg = f"Max J: {maxIntenJ:.0f}"
    if tkplot:
        widget = FELion_Tk(title="Boltzman distribution", location=location)
        fig, canvas = widget.Figure()
        ax = widget.make_figure_layout(title=f"Boltzman distribution at T:{temp:.1f}K; Z: {Z:.2f}",
            xaxis="Rotation levels (J)", yaxis="Population (%)", savename=f"boltzman_distribution_{temp:.0f}K")
        ax.plot(totalJ, distribution, ".-" ,label=lg)

        ax.set_xticks(totalJ)
        widget.set_minor(1)
        widget.plot_legend = ax.legend()
        widget.mainloop()
    else: 
        
        dataToSend = {"distribution": {"x": totalJ.tolist(), "y": distribution.tolist(), "name": f"{lg} at {temp:.1f}K; Z: {Z:.2f}; Total: {distribution.sum():.2f}%", "mode": "lines+markers", "showlegend":True}}
        sendData(dataToSend)

    
if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    location = pt(args[0])
    os.chdir(location)
    B0 = float(args[1])
    D0 = float(args[2])
    H0 = float(args[3])
    temp = float(args[4])
    totalJ = int(args[5])

    tkplot = args[6]
    if tkplot == "plot": tkplot = True
    else: tkplot = False
    calculate_population(B0, D0, H0, temp, totalJ, tkplot, location)