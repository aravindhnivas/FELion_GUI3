
import sys, json, pprint
from pathlib import Path as pt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
np.seterr(invalid="ignore")

main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)
from FELion_definitions import sendData
from FELion_constants import pltColors

def linearFit(x, m, c): return m*x + c

def collisionalFit():

    fullname = pt(args["collisionalFilename"])


    with open(fullname, "r") as f:
        data_info = f.readlines()

    data = []
    for line in data_info:
        if not "#" in line:
            if len(line) > 1:
                line = line.strip()
                line = line.split("\t")
                data.append(line)

    temperature = np.array(data[0], dtype=float)
    fitTemp = np.arange(1, temperature[-1]+0.1, 1)
    collisionalTemp = float(args["collisionalTemp"])
    collisionalRateType = args["collisionalRateType"]
    dataToSend = {"type" : collisionalRateType, "rateConstants" : []}

    fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

    size = 2+len(temperature)
    for counter, rate in enumerate(data[1:]):
        i, j = rate[:2]
        

        rateConstants = np.array(rate[2:size], dtype=float)
        ax.plot(temperature, rateConstants, ".", c=pltColors[counter])
        pop, pcov = curve_fit(linearFit, temperature, rateConstants)
        perr = np.diag(np.sqrt(pcov))

        lg = f"{i.strip()} --> {j.strip()}"
        # lg += f" [m={pop[0]:.1f}({perr[0]:.1f}), c={pop[1]:.1f}({perr[1]:.1f})]"
        ax.plot(fitTemp, linearFit(fitTemp, *pop), "-", c=pltColors[counter], label=lg)

        _requiredRate = {"label": lg, "value": float(linearFit(collisionalTemp, *pop))}

        dataToSend["rateConstants"].append(_requiredRate)
    ax.legend()

    ax.set(xlabel="Temp (K)", ylabel="k$_{jj'}$ (cm$^3$ molecule$^{-1}$ s$^{-1}$)", title="Collisional rate constants", yscale="log")

    # saveFilename = args["saveFilename"]

    # with open(fullname.parent/f"{saveFilename}_{requiredTemp}K.json", 'w+') as f:
    #     saveData = json.dump(dataToSend, f, sort_keys=True, indent=4, separators=(',', ': '))
    sendData(dataToSend, calling_file=pt(__file__).stem)
    # plt.show()

args = None
def main(arguments):

    global args
    args = arguments
    # args = json.loads(sys.argv[1])
    print(args, flush=True)

    pp = pprint.PrettyPrinter(indent=4)
    
    collisionalFit()