
import sys
import json
# import traceback
from pprint import PrettyPrinter
# import numpy as np
import matplotlib.pyplot as plt
from optimizePlot import optimizePlot
from pathlib import Path as pt
from FELion_definitions import readCodeFromFile
from symfit import variables, Parameter, ODEModel, D, Fit, parameters, Variable


def codeToRun(code):
    exec(code)
    return locals()




ode_model = None

def runKineticCode():
    
    global ode_model

    location = pt(args["kineticEditorLocation"])
    filename = pt(location) / args["kineticEditorFilename"]
    codeContents = readCodeFromFile(filename)
    codeOutput = codeToRun(codeContents)
    ode_model = codeOutput["ode_model"]
    # print(codeOutput, flush=True)
    # print(f"{ode_model=}", flush=True)
    return

fig, ax = None, None

def plotFigure():
    
    global fig, ax
    fig, ax = plt.subplots()
    counter = 0

    for key, data in args["data"].items():
        ax.errorbar(time, data["y"], yerr=data["error_y"]["array"], label=key, fmt=".-", c=f"C{counter}")
        counter += 1
    ax = optimizePlot(ax, "Time (ms)", "Counts", "log")
    return

if __name__ == "__main__":
    args = json.loads(sys.argv[1])
    pp = PrettyPrinter(indent=4)

    # pp.pprint(args)

    nameOfReactants = args["nameOfReactantsArray"]
    time = args["data"][nameOfReactants[0]]["x"]

    runKineticCode()
    plotFigure()
    plt.show()

    