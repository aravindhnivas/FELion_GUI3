
import sys, json, pprint
from pathlib import Path as pt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
np.seterr(invalid="ignore")

import yaml

main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)

from FELion_definitions import sendData

from FELion_constants import pltColors

def linearFit(x, m, c): return m*x + c


def collisionalFit():

    fullname = pt(args["collisionlFile"])
    data = np.genfromtxt(fullname)
    temperature = data[0][2:]

    fitTemp = np.arange(1, temperature[-1], 1)
    requiredTemp = float(args["requiredTemp"])
    collisionalRateType = args["collisionalRateType"]
    requiredRate = {"type" : collisionalRateType, "rateConstants" : []}
    dataToSend = {}
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

    for counter, rate in enumerate(data[1:]):
        print(f"{rate=}", flush=True)
        i, j = rate[:2]
        
        rateConstants = rate[2:]
        ax.plot(temperature, rateConstants, ".", c=pltColors[counter])
        pop, pcov = curve_fit(linearFit, temperature, rateConstants)
        perr = np.diag(np.sqrt(pcov))

        lg = f"{i} --> {j}"
        # lg += f" [m={pop[0]:.1f}({perr[0]:.1f}), c={pop[1]:.1f}({perr[1]:.1f})]"


        ax.plot(fitTemp, linearFit(fitTemp, *pop), "-", c=pltColors[counter], label=lg)
        _requiredRate = {"label": lg, "value": float(linearFit(requiredTemp, *pop))}
        requiredRate["rateConstants"].append(_requiredRate)

    ax.legend()
    saveFilename = args["saveFilename"]

    with open(fullname.parent/f"{saveFilename}_{requiredTemp}K.yml", 'w+') as f:
        saveData = yaml.dump(requiredRate, f)

    sendData(saveData)

if __name__ == "__main__":
    args = json.loads(sys.argv[1])
    print(args, flush=True)
    pp = pprint.PrettyPrinter(indent=4)
    collisionalFit()