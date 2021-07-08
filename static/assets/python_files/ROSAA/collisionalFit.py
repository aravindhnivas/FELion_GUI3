
import sys, json, pprint
from pathlib import Path as pt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
np.seterr(invalid="ignore")

# import yaml

main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)

from FELion_definitions import sendData

from FELion_constants import pltColors

def linearFit(x, m, c): return m*x + c


def collisionalFit():

    fullname = pt(args["collisionlFile"])
    with open(fullname, "r") as f:
        data_info = f.readlines()
    
    # print(data_info, flush=True)
    data = []
    for line in data_info:
        if not "#" in line:
            if len(line) > 1:
                line = line.strip()
                line = line.split("\t")
                data.append(line)
                # print(data, flush=True)

    # data = np.genfromtxt(fullname)
    temperature = np.array(data[0], dtype=float)

    fitTemp = np.arange(1, temperature[-1], 1)
    requiredTemp = float(args["requiredTemp"])
    collisionalRateType = args["collisionalRateType"]
    dataToSend = {"type" : collisionalRateType, "rateConstants" : []}
    # dataToSend = {}
    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

    for counter, rate in enumerate(data[1:]):
        # print(f"{rate=}", flush=True)
        i, j = rate[:2]
        
        rateConstants = np.array(rate[2:], dtype=float)
        ax.plot(temperature, rateConstants, ".", c=pltColors[counter])
        pop, pcov = curve_fit(linearFit, temperature, rateConstants)
        perr = np.diag(np.sqrt(pcov))

        lg = f"{i.strip()} --> {j.strip()}"
        # lg += f" [m={pop[0]:.1f}({perr[0]:.1f}), c={pop[1]:.1f}({perr[1]:.1f})]"


        ax.plot(fitTemp, linearFit(fitTemp, *pop), "-", c=pltColors[counter], label=lg)
        _requiredRate = {"label": lg, "value": float(linearFit(requiredTemp, *pop))}
        dataToSend["rateConstants"].append(_requiredRate)

    ax.legend()

    saveFilename = args["saveFilename"]

    # with open(fullname.parent/f"{saveFilename}_{requiredTemp}K.yml", 'w+') as f:
    #     saveData = json.dump(dataToSend, f, sort_keys=True, indent=4, separators=(',', ': '))
    sendData(dataToSend)

if __name__ == "__main__":

    args = json.loads(sys.argv[1])
    print(args, flush=True)
    
    pp = pprint.PrettyPrinter(indent=4)

    collisionalFit()