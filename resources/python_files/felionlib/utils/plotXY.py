from pathlib import Path as pt
import json
from felionlib.utils.felionQt import felionQtWindow
from felionlib.utils.FELion_constants import pltColors

widget: felionQtWindow = None


def plotFromJSON(fileName: str, legend_handler: dict = None):

    with open(fileName, "r") as f:
        data = json.load(f)
        counter = 0

        for key, value in data.items():

            x = value["x"]
            y = value["y"]

            plot_args = ()
            plot_kwargs = {}

            if "plot_args" in value:
                plot_args = value["plot_args"]
            if "plot_kwargs" in value:
                plot_kwargs = value["plot_kwargs"]

            if "color" not in plot_kwargs:
                plot_kwargs["color"] = pltColors[counter]

            if "label" not in plot_kwargs:
                plot_kwargs["label"] = f"{legend_prefix}{key}{legend_suffix}"

            (legend_handler[plot_kwargs["label"]],) = widget.ax.plot(x, y, *plot_args, **plot_kwargs)
            counter += 1


legend_prefix = ""
legend_suffix = ""


def main(args):

    global widget, legend_prefix, legend_suffix

    files = [pt(i) for i in args["files"]]
    figArgs = args["figArgs"]
    legend_prefix = args["legend_prefix"]
    legend_suffix = args["legend_suffix"]

    widget = felionQtWindow(**figArgs)
    legend_handler = {}

    for file in files:
        if file.suffix == ".json":
            plotFromJSON(file, legend_handler)
            continue

        x, y = [], []
        with open(file, "r") as f:
            for line in f.readlines():
                if line.startswith("#"):
                    continue
                data = line.split()

                if "x_type" in figArgs and figArgs["x_type"] == "float":
                    x.append(float(data[0]))
                else:
                    x.append(data[0])

                if "y_type" in figArgs and figArgs["y_type"] == "float":
                    y.append(float(data[1]))
                else:
                    y.append(data[1])

        if "labels" in figArgs and figArgs["labels"][file.name]:
            label = figArgs["labels"][file.name]
        else:
            label = file.stem

        (legend_handler[label],) = widget.ax.plot(x, y, label=label)

    widget.makeLegendToggler(legend_handler, edit_legend=True)
    widget.optimize_figure()
    widget.fig.tight_layout()
    widget.qapp.exec()
