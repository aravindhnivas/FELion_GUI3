from collections import namedtuple
from dataclasses import dataclass, field
from pathlib import Path as pt
from typing import Literal, NamedTuple
from matplotlib.axes import Axes
import numpy as np
from felionlib.utils.felionQt import felionQtWindow
from typing import Iterable
from .definitions import computeNGaussian
# from matplotlib.container import Container
from matplotlib.artist import Artist

logger = lambda *args, **kwargs: print(*args, **kwargs, flush=True)
methods_available: list[str] = ["Log", "Relative", "IntensityPerPhoton"]


@dataclass(slots=True)
class NumberWidgets:
    freqScale: float
    theorySigma: float
    
@dataclass(slots=True)
class BooleanWidgets:
    Only_exp: bool
    
@dataclass(slots=True)
class TextWidgets:
    Cal_title: str
    Exp_legend: str
    Exp_title: str
    
@dataclass(slots=True)
class SelectedWidgets:
    Fundamentals: list[str]
    Combinations: list[str]
    Overtones: list[str]
    Others: list[str]
    DAT_file: list[str]
    
@dataclass(slots=True)
class Args:
    location: str
    theoryLocation: str
    normMethod: str
    numberWidgets: NumberWidgets
    textWidgets: TextWidgets
    booleanWidgets: BooleanWidgets
    selectedWidgets: SelectedWidgets
    
    def __post_init__(self):
        self.numberWidgets = NumberWidgets(**self.numberWidgets)
        self.booleanWidgets = BooleanWidgets(**self.booleanWidgets)
        self.textWidgets = TextWidgets(**self.textWidgets)
        self.selectedWidgets = SelectedWidgets(**self.selectedWidgets)
    
    
@dataclass(slots=True)
class PlotData:
    args: Args
    widget: felionQtWindow
    data_location: pt
    axes: list[Axes] = field(default_factory=list)
    Only_exp: bool = field(init=False)
    export_location: pt = field(init=False)
    ax_exp: Axes = field(init=False)
    ax_theory: Axes = field(init=False)
    exp_legend: str = field(init=False)
    exp_files: list[str] = field(init=False)
    yind: Literal[0, 1, 2] = field(init=False)
    normMethod: Literal["Log", "Relative", "IntensityPerPhoton"] = field(init=False)
    line_handler: dict[str, Artist | Iterable] = field(default_factory=dict)
    
    def __post_init__(self):
        
        if self.args.booleanWidgets.Only_exp:
            
            self.ax_exp = self.widget.fig.subplots(1)
            self.axes = (self.ax_exp, )
            self.ax_theory = None
        else:
            self.ax_exp, self.ax_theory = self.widget.fig.subplots(2, 1, sharex=True)
            self.axes = self.ax_exp, self.ax_theory
        
        self.export_location = self.data_location / "../EXPORT"
        self.normMethod = self.args.normMethod
        self.yind = methods_available.index(self.normMethod)
        self.exp_files = self.args.selectedWidgets.DAT_file
        
        self.exp_legend = self.args.textWidgets.Exp_legend.split(",")
        if len(self.exp_legend) != len(self.exp_files):
            self.exp_legend = [f"{filename.replace('.dat', '')}" for filename in self.exp_files]
        
    def plot(self):
        
        self.widget.createControlLayout(self.axes, attachControlLayout=True)
        if not self.args.booleanWidgets.Only_exp: self.toggle_axes()
        
        self.plot_exp()
        self.plot_make_labels()
        if not self.args.booleanWidgets.Only_exp: self.plot_theory()
        
    def toggle_axes(self):

        self.ax_exp.tick_params("x", which="both", bottom=False, labelbottom=False, top=True, labeltop=True,)
        self.ax_exp.tick_params("y", which="both", right=True)
        self.ax_exp.spines["bottom"].set_visible(False)
        if self.ax_theory:
            self.ax_theory.tick_params("x", which="both", top=False, labeltop=False)
            self.ax_theory.spines["top"].set_visible(False)
            self.ax_theory.tick_params("y", which="both", right=True)
            self.ax_theory.invert_yaxis()

    def plot_this_exp_file(self, filename: str, color="C0", label: str = 'legend'):
        
        fullfile = self.export_location / filename
        fullfitfile = self.export_location / f"{fullfile.stem}_{self.normMethod}.fullfit"

        if fullfile.exists():
            
            data: np.ndarray = np.genfromtxt(fullfile).T
            wn = data[0]
            inten = data[self.yind+1]

            current_plot_handle_exp_fill = self.ax_exp.fill_between(
                wn, inten,
                alpha=0.5 if fullfitfile.exists() else 1,
                color=color, ec="none", step="pre",
                label=label
            )
            
            self.ax_exp.legend(title=self.args.textWidgets.Exp_title)
            self.line_handler[label] = current_plot_handle_exp_fill
            
            if fullfitfile.exists():
                simulate_exp_data = np.genfromtxt(fullfitfile).T
                similated_freq, simulated_inten = simulate_exp_data
                fit_label = f"fit_{label}"
                (current_plot_handle_fit,) = self.ax_exp.plot(
                    similated_freq, simulated_inten, "-", c=color, lw=1.1, label=fit_label
                )
                self.line_handler[fit_label] = current_plot_handle_fit
            
    
    def plot_make_labels(self):
        xlabel="Wavenumber [cm$^{-1}$]"
        if self.ax_theory:
            self.ax_theory.set(
                xlabel=xlabel, ylabel="Intensity [Km/mol]"
            )
            
        self.ax_exp.set(
            xlabel=xlabel if self.args.booleanWidgets.Only_exp else "",
            ylabel=("Norm. Intensity ~[m$^2$/photon]", "Relative Depletion [%]")[self.normMethod=="Relative"],
        )

    def plot_exp(self):
        for index, filename in enumerate(self.exp_files):
            self.plot_this_exp_file(filename, color=f"C{index}", label=self.exp_legend[index])
            
        self.ax_exp.set_ybound(lower=-5)

    def plot_this_theory_file(self, filename: str | list[str] | tuple[str], color=None, **kwargs):
        if not filename: return
        if isinstance(filename, list | tuple):
            for i, f in enumerate(filename):
                color = f"C{len(self.exp_files) + i}"
                self.plot_this_theory_file(f, color, **kwargs)
            return
        
        if not color: color = f"C{len(self.exp_files) + 1}"
        
        fullfile = pt(self.args.theoryLocation) / filename
        fileData: list[str] = None
        with open(fullfile, "r") as fp:
            fileData = fp.readlines()
        
        label = fileData[1].split("#")[-1].strip()
        wn, inten = np.genfromtxt(fullfile).T
        wn *= self.args.numberWidgets.freqScale
        
        simulatedData = computeNGaussian(wn, inten, sigma=self.args.numberWidgets.theorySigma)
        (current_plot_theory,) = self.ax_theory.plot(*simulatedData, f"{color}", label=label, **kwargs)
        self.line_handler[label] = current_plot_theory
    
    def plot_theory(self):
        self.plot_this_theory_file(self.args.selectedWidgets.Fundamentals, ls='solid')
        self.plot_this_theory_file(self.args.selectedWidgets.Others, ls='dashed')
        self.plot_this_theory_file(self.args.selectedWidgets.Combinations, ls='dashdot')
        
        self.plot_this_theory_file(self.args.selectedWidgets.Overtones, ls='dotted')
        self.ax_theory.legend(title=self.args.textWidgets.Cal_title)
        self.ax_theory.set_ybound(lower=-5)


def main(args):
    
    args = Args(**args)
    print(f"{args=}", flush=True)
    data_location = pt(args.location)
    out_location = data_location / "../OUT"
    widget = felionQtWindow(title="FELIX Spectrum", location=out_location, 
        ticks_direction="in", createControlLayout=False, windowGeometry=(1000, 700)
    )
    plotData = PlotData(args, widget, data_location)
    plotData.plot()

    widget.makeLegendToggler(plotData.line_handler, edit_legend=True)
    widget.optimize_figure()
    widget.updatecanvas()
    widget.qapp.exec()
    