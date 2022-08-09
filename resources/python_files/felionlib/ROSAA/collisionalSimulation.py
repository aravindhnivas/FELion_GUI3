import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from felionlib.utils.FELion_definitions import sendData
from felionlib.utils.FELion_constants import colors


def collisionalRateDistribution(t, N):
    rateCollection = []
    N = {key: value for key, value in zip(energyKeys, N)}
    rateCollection = []

    for i in energyKeys:
        collisional = []

        for j in energyKeys:

            selectionRule = i != j
            if "_" in str(i):
                selectionRule = i.split("_")[0] != j.split("_")[0]

            if selectionRule:
                key = f"{j} --> {i}"
                keyInverse = f"{i} --> {j}"
                k = rate_constants[key] * nHe * N[j] - rate_constants[keyInverse] * nHe * N[i]
                collisional.append(k)
        collisional = np.sum(collisional)
        rateCollection.append(collisional)

    return rateCollection


def simulate(args):
    time = float(args["duration"]) * 1e-3

    tspan = [0, time]
    simulateTime = np.linspace(0, time, 100)

    N_collisional = solve_ivp(
        collisionalRateDistribution, tspan, boltzmanDistributionInitial, method="Radau", t_eval=simulateTime
    )

    print(f"{N_collisional.nfev=} evaluations required.", flush=True)
    simulateCounts = N_collisional.y
    data = simulateCounts.tolist()
    defaultStyle = {"mode": "lines+markers", "fill": "tozeroy", "marker": {"size": 1}}

    dataWithLabel = {}
    colorIndex = 0
    for key, value in zip(energyKeys, data):

        lineColor = {"color": f"rgb{colors[colorIndex]}"}
        dataWithLabel[key] = {"x": simulateTime.tolist(), "y": value, "name": key, **defaultStyle, **lineColor}
        colorIndex += 2
    collisionalDistribution = simulateCounts.T[-1]

    differenceFromBoltzman = np.around(collisionalDistribution - boltzmanDistributionCold, decimals=2)
    dataToSend = {
        "data": dataWithLabel,
        "collisionalBoltzmanPlotData": {
            "collisionalData": {"x": energyKeys, "y": collisionalDistribution.tolist(), "name": "collisional"},
            "boltzmanData": {"x": energyKeys, "y": boltzmanDistributionCold.tolist(), "name": "Boltzman"},
        },
        "differenceFromBoltzman": {
            "data": {"x": energyKeys, "y": differenceFromBoltzman.tolist(), "name": "Difference"}
        },
    }

    return sendData(dataToSend, calling_file=pt(__file__).stem)


def plot(simulateTime, simulateCounts):

    _, ax = plt.subplots(figsize=(7, 4), dpi=100)
    ax.plot(simulateTime.T * 1e3, simulateCounts.T)
    ax.plot(simulateTime * 1e3, simulateCounts.sum(axis=0), "k")
    ax.legend([*[f"J{i}" for i in energyKeys], "SUM"], title=f"He: {nHe:.2e}cm3")

    sourceTemp = 300
    trapTemp = 10

    ax.set(
        xlabel="Time (ms)",
        ylabel="Population (%)",
        title="Simulation: Thermal stabilisation by collision with $^4$He atoms " + f"({sourceTemp}K => {trapTemp}K)",
    )
    plt.show()


rate_constants = None
nHe = None

boltzmanDistributionInitial = None
boltzmanDistributionCold = None
energyKeys = None


def main(args):

    global rate_constants, nHe, boltzmanDistributionInitial, energyKeys, boltzmanDistributionCold
    numberOfLevels = int(args["numberOfLevels"])

    rate_constants = {key: float(value) for key, value in args["collisionalRateConstantValues"].items()}
    nHe = float(args["numberDensity"])

    boltzmanDistribution = args["boltzmanDistributionValues"].values()
    boltzmanDistributionInitial = np.array(list(boltzmanDistribution)[:numberOfLevels], dtype=float)

    boltzmanDistributionCold = args["boltzmanDistributionColdValues"].values()
    boltzmanDistributionCold = np.array(list(boltzmanDistributionCold)[:numberOfLevels], dtype=float)

    energyKeys = args["energyKeys"][:numberOfLevels]

    simulate(args)
