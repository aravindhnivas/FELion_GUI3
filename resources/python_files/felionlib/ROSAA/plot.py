import json
import numpy as np
from pathlib import Path as pt
# import matplotlib.pyplot as plt
from felionlib.utils.felionQt import felionQtWindow


def read_json(directory, type="f-power") -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    directory = pt(directory)
    datas = []
    for filename in directory.glob("*.json"):
        data = json.load(open(filename))
        datas.append(data)

    variable_name = "power" if type == "f-power" else "numberDensity"
    constant_name = "numberDensity" if type == "f-power" else "power"

    X = np.array([data[f"variable ({variable_name})"] for data in datas], dtype=float)
    Y = np.array(
        [
            [data["constant"][f"{constant_name}"][0]] * len(data[f"variable ({variable_name})"]) 
            for data in datas
        ],
        dtype=float
    )
    
    Z = np.array([data["signalChange"] for data in datas], dtype=float)
    # if "signalChange" in datas[0]:
    #     Z = np.array([data["signalChange"] for data in datas], dtype=float)
    # else:
    #     Z = np.array([data["populationChange"] for data in datas], dtype=float)

    if type == "f-power":
        return X, Y, Z
    else:
        return Y, X, Z


def main(directory: pt, type="f-power") -> None:

    if not directory.exists():
        raise FileNotFoundError(f"{directory} does not exist")

    print(f"{directory=}", flush=True)
    widget = felionQtWindow(
        figDPI=200,
        location=directory / "figs",
        xscale="linear",
        createControlLayout=False,
        figureArgs=dict(figsize=(12, 8)),
    )

    ax = widget.fig.add_subplot(111, projection="3d")
    # fig = plt.figure(figsize=(12, 8))
    # ax = fig.add_subplot(111, projection="3d")
    X, Y, Z = read_json(directory, type=type)
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap="viridis", edgecolor="none")
    ax.set_xlabel("Power (W)", labelpad=20)
    ax.set_ylabel("Number Density (cm$^{-3}$)", labelpad=20)
    ax.set_zlabel("Signal (%)", labelpad=20)

    widget.createControlLayout(axes=(ax,), optimize=True)
    widget.fig.tight_layout()
    widget.qapp.exec()
    # plt.show()
    