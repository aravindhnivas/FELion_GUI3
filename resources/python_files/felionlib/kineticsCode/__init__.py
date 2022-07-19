from pathlib import Path as pt
import numpy as np
from felionlib.utils.felionQt import felionQtWindow
from .utils.configfile import read_config
from uncertainties import ufloat_fromstr
from felionlib.utils.FELion_definitions import readCodeFromFile

tspan: list[float, float] = None
simulateTime: np.ndarray = None
plotted = False


def KineticMain():
    global tspan, simulateTime, plotted

    duration = expTime.max() * 1.2
    tspan = [0, duration]
    simulateTime = np.linspace(0, duration, 1000)

    from .utils.plot import plot_exp
    from .utils.plotWidgets import make_widgets

    plotted = False
    plot_exp()
    make_widgets()
    plotted = True


temp: str = None
selectedFile: str = None
nameOfReactants: str = None
numberDensity: float = None
widget: felionQtWindow = None
nameOfReactantsArray: list[str] = None
kinetic_plot_adjust_configs_obj: dict[str, float] = {}
legends: list[str] = []
kinetics_equation_file: pt = None
data: dict[str, dict] = {}
useTaggedFile: bool = None
tagFile: str = None
kineticCodeContents: str = None


def main(args):

    global data, widget, legends
    global useTaggedFile, tagFile
    global kinetic_plot_adjust_configs_obj, kineticCodeContents
    global temp, numberDensity, kinetics_equation_file
    global totalAttachmentLevels, selectedFile, initialValues
    global kinetic_file_location, nameOfReactants, expTime, expData, expDataError

    kinetic_file_location = pt(args["kinetic_file_location"])
    kinetics_equation_file = kinetic_file_location / args["kineticEditorFilename"]
    kineticCodeContents = readCodeFromFile(kinetics_equation_file)
    # print(f"{args['kineticEditorFilename']=}\n{kinetics_equation_file=}", flush=True)

    # return
    config_files_location = kinetic_file_location.parent / "configs"

    if not config_files_location.exists():
        config_files_location.mkdir()

    data = args["data"]
    useTaggedFile = args["useTaggedFile"]
    tagFile = args["tagFile"]
    nameOfReactants = args["nameOfReactantsArray"]

    expTime = np.array(data[nameOfReactants[0]]["x"], dtype=float) * 1e-3  # ms --> s
    expData = np.array([data[name]["y"] for name in nameOfReactants], dtype=float)
    expDataError = np.array([data[name]["error_y"]["array"] for name in nameOfReactants], dtype=float)

    print(f"{expDataError.shape=}", flush=True)

    selectedFile = args["selectedFile"]

    try:
        numberDensity = ufloat_fromstr(args["numberDensity"])
        print(f"{numberDensity=}", flush=True)
    except Exception as error:
        print(f"Could not read number density", error, flush=True)

    initialValues = [float(i) for i in args["initialValues"]]
    totalAttachmentLevels = len(initialValues) - 1

    outdir = kinetic_file_location.parent / "OUT"
    fit_config_file = config_files_location / args["$fit_config_filename"]

    legends = [lg.strip() for lg in args["legends"].split(",")]
    read_config(fit_config_file, selectedFile, kineticCodeContents, useTaggedFile, tagFile)

    kinetic_plot_adjust_configs_obj = {
        key: float(value) for key, value in args["kinetic_plot_adjust_configs_obj"].items()
    }
    if not kinetic_plot_adjust_configs_obj:
        kinetic_plot_adjust_configs_obj = {"right": 0.570, "top": 0.900, "left": 0.120, "bottom": 0.160}

    widget = felionQtWindow(title=f"kinetics : {selectedFile}", windowGeometry=(1200, 600), location=outdir)
    KineticMain()
    widget.ax.set_ybound(lower=1)
    widget.optimize_figure()
    widget.qapp.exec()
