from pathlib import Path as pt
import numpy as np
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
np.seterr(invalid="ignore")

from FELion_definitions import sendData
from FELion_constants import pltColors

def linearFit(x, m, c): return m*x + c

def main(args):

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
    fitTemp = np.linspace(temperature[0], temperature[-1], 30)
    collisionalTemp = float(args["collisionalTemp"])
    dataToSend = {"original": {}, "fit": {}, f"{collisionalTemp}K": {}}

    _, ax = plt.subplots(figsize=(10, 6), dpi=100)

    size = 2+len(temperature)

    for counter, rate in enumerate(data[1:]):

        i, j = rate[:2]
        lg = f"{i.strip()} --> {j.strip()}"


        rateConstants = np.array(rate[2:size], dtype=float)
        ax.plot(temperature, rateConstants, ".", c=pltColors[counter])

        dataToSend["original"][lg] = {
            "temperature": temperature.tolist(),
            "rateConstants": rateConstants.tolist(),
        }
        pop, pcov = curve_fit(linearFit, temperature, rateConstants)
        perr = np.diag(np.sqrt(pcov))

        fitRateConstants = linearFit(fitTemp, *pop)
        ax.plot(fitTemp, fitRateConstants, "-", c=pltColors[counter], label=lg)


        dataToSend["fit"][lg] = {
            "temperature": fitTemp.tolist(),
            "rateConstants": fitRateConstants.tolist(),
            "parameters": f"m={pop[0]:.1f}({perr[0]:.1f}), c={pop[1]:.1f}({perr[1]:.1f})"

        }

        dataToSend[f"{collisionalTemp}K"][lg] = float(linearFit(collisionalTemp, *pop))

    ax.legend()

    ax.set(xlabel="Temp (K)", ylabel="k$_{jj'}$ (cm$^3$ molecule$^{-1}$ s$^{-1}$)", title="Collisional rate constants", yscale="log")
    sendData(dataToSend, calling_file=pt(__file__).stem)

    plt.show()
