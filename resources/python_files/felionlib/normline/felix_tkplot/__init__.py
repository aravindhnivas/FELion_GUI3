from dataclasses import dataclass, field
from pathlib import Path as pt
from typing import Any, Literal, Optional
from matplotlib.axes import Axes
import numpy as np
from felionlib.utils.felionQt import felionQtWindow
from .definitions import computeNGaussian

logger = lambda *args, **kwargs: print(*args, **kwargs, flush=True)
methods_available: list[str] = ["Log", "Relative", "IntensityPerPhoton"]

# 

@dataclass(slots=True)
class PlotData:
    args: dict[str, Any]
    widget: felionQtWindow
    data_location: pt
    axes: list[Axes] = field(default_factory=list)
    Only_exp: bool = field(init=False)
    export_location: pt = field(init=False)
    ax_exp: Axes = field(init=False)
    ax_theory: Axes = field(init=False)
    exp_legend_title: str = field(init=False)
    theory_legend_title: str = field(init=False)
    exp_legend: str = field(init=False)
    exp_files: list[str] = field(init=False)
    yind: Literal[0, 1, 2] = field(init=False)
    normMethod: Literal["Log", "Relative", "IntensityPerPhoton"] = field(init=False)
    theoryLocation: pt =  field(init=False)
    freqScale: float = field(init=False)
    theorySigma: float = field(init=False)
    fundamental_theory_file: list[str] = field(init=False)
    combination_overtons_files: list[str] =  field(init=False)
    
    
    def __post_init__(self):
        self.Only_exp = self.args["booleanWidgets"]["Only_exp"]
        if self.Only_exp:
            self.ax_exp = self.widget.fig.subplots(1)
            self.axes = (self.ax_exp, )
            self.ax_theory = None
        else:
            self.ax_exp, self.ax_theory = self.widget.fig.subplots(2, 1, sharex=True)
            self.axes = self.ax_exp, self.ax_theory
        
        self.exp_legend_title = self.args["textWidgets"]["Exp_title"]
        self.exp_legend = self.args["textWidgets"]["Exp_legend"]
        self.theory_legend_title = self.args["textWidgets"]["Cal_title"]
        self.export_location = self.data_location / "../EXPORT"
        
        self.normMethod = self.args["normMethod"]
        self.yind = methods_available.index(self.normMethod)
        self.exp_files = self.args["selectedWidgets"]["DAT_file"]
        
        if self.ax_theory:
            self.theoryLocation = pt(self.args["theoryLocation"])
            self.freqScale = float(self.args["numberWidgets"]["freqScale"])
            self.theorySigma = float(self.args["numberWidgets"]["theorySigma"])
            self.fundamental_theory_file: list[str] = self.args["selectedWidgets"]["Fundamentals"]
            self.combination_overtons_files: list[str] = self.args["selectedWidgets"]["Combinations + Overtones"]
        
    def plot(self):
        logger(self.args["booleanWidgets"])
        self.widget.createControlLayout(self.axes, attachControlLayout=True)

        if not self.Only_exp: self.toggle_axes()
        
        self.plot_exp()
        self.plot_make_labels()
        if not self.Only_exp: self.plot_theory()

    def toggle_axes(self):

        self.ax_exp.tick_params("x", which="both", bottom=False, labelbottom=False, top=True, labeltop=True,)
        self.ax_exp.tick_params("y", which="both", right=True)
        self.ax_exp.spines["bottom"].set_visible(False)
        if self.ax_theory:
            self.ax_theory.tick_params("x", which="both", top=False, labeltop=False)
            self.ax_theory.spines["top"].set_visible(False)
            self.ax_theory.tick_params("y", which="both", right=True)
            self.ax_theory.invert_yaxis()

    def plot_this_exp_file(self, filename: str, color="C0"):
        
        fullfile = self.export_location / filename
        fullfitfile = self.export_location / f"{fullfile.stem}_{self.normMethod}.fullfit"

        if fullfile.exists():
            
            data: np.ndarray = np.genfromtxt(fullfile).T
            wn = data[0]
            inten = data[self.yind+1]

            self.ax_exp.fill_between(
                wn, inten,
                alpha=0.3 if fullfitfile.exists() else 1,
                color=color, ec="none", step="pre"
            )

            if fullfitfile.exists():
                simulate_exp_data = np.genfromtxt(fullfitfile).T

                similated_freq, simulated_inten = simulate_exp_data
                self.ax_exp.plot(similated_freq, simulated_inten, "-", c=color, lw=1.1, label=self.exp_legend)

            self.ax_exp.legend(title=self.exp_legend_title)
    
    def plot_make_labels(self):

        if self.ax_theory:
            self.ax_theory.set(
                xlabel="Wavenumber (cm$^{-1}$)",
                ylabel="Intensity (Km/mol)"
            )
        self.ax_exp.set(
            xlabel="Wavenumber (cm$^{-1}$)" if self.Only_exp else "",
            ylabel=("Norm. Intensity ~(m$^2$/photon)", "Relative Depletion (%)")[self.normMethod=="Relative"],
        )

    def plot_exp(self):
        
        if len(self.exp_files) == 1:
            filename = self.exp_files[0]
            self.plot_this_exp_file(filename)
        else:
            for index, filename in enumerate(self.exp_files):
                self.plot_this_exp_file(filename, color=f"C{index}")

    def plot_this_theory_file(self, filename, color, ls='-'):
        fullfile = self.theoryLocation / filename
        fileData: list[str] = None

        with open(fullfile, "r") as fp:
            fileData = fp.readlines()
        
        label = fileData[0].split("#")[-1].strip()
        # self.theory_legends.append(theory_level)
        # molecule_name = fileData[1].split("#")[-1].strip()
        wn, inten = np.genfromtxt(fullfile).T
        wn *= self.freqScale
        simulatedData = computeNGaussian(wn, inten, sigma=self.theorySigma)
        (local_ax,) = self.ax_theory.plot(*simulatedData, f"{ls}{color}", label=label)
        # self.ax_theory.legend(self.theory_legends, title=self.theory_legend_title)
        
        return local_ax
    
    def plot_theory(self):
        
        for index, filename in enumerate(self.fundamental_theory_file):
            self.plot_this_theory_file(filename, color=f"C{len(self.exp_files) + index}")
        
        for index, filename in enumerate(self.combination_overtons_files):
            self.plot_this_theory_file(filename, color=f"C{len(self.exp_files) + index}", ls='--')
        
        
        self.ax_theory.legend(title=self.theory_legend_title)

def main(args):
    data_location = pt(args["location"])
    
    out_location = data_location / "../OUT"
    widget = felionQtWindow(title="FELIX Spectrum", location=out_location, ticks_direction="in", createControlLayout=False, windowGeometry=(1000, 700))
    
    plotData = PlotData(args, widget, data_location)
    plotData.plot()

    widget.optimize_figure()
    widget.updatecanvas()
    widget.qapp.exec()
        