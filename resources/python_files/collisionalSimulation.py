
import sys, json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from FELion_definitions import sendData

from FELion_constants import colors

from functools import reduce
def collisionalRateDistribution(t, N):

    rateCollection = []
    N = {key: value for key, value in zip(energyKeys, N)}
    rateCollection = []
    # print(f"{N=}", flush=True)
    for i in energyKeys:
        collisional = []

        for j in energyKeys:
            if i!= j and i.split("_")[0] != j.split("_")[0]: 
                
                key = f"{j} --> {i}"
                keyInverse = f"{i} --> {j}"

                # print(f"{key}\n{keyInverse}", flush=True)

                k = rate_constants[key]*nHe*N[j] - rate_constants[keyInverse]*nHe*N[i]
                collisional.append(k)
        rateCollection.append(collisional)
    
    dR_dt = []
    for _ in rateCollection:
        temp = reduce(lambda a, b: a+b, _)
        dR_dt.append(temp)
    return dR_dt
    

def simulate(args):

    time = float(args["duration"])*1e-3

    tspan = [0, time]
    N_collisional = solve_ivp(collisionalRateDistribution, tspan, boltzmanDistributionInitial, dense_output=True)
    simulateTime = np.linspace(0, time, 100)


    simulateCounts = N_collisional.sol(simulateTime)

    data = simulateCounts.tolist()
    defaultStyle={"mode": "lines+markers", "fill": 'tozeroy', "marker": {"size":1}}
    
    dataWithLabel = {}
    colorIndex = 0
    for key, value in zip(energyKeys, data):

        lineColor = {"color": f"rgb{colors[colorIndex]}"}

        dataWithLabel[key] = {"x":simulateTime.tolist(), "y":value, "name":key, **defaultStyle, **lineColor}
        colorIndex += 2

    collisionalDistribution = simulateCounts.T[-1]
    
    differenceFromBoltzman = np.around(collisionalDistribution - boltzmanDistributionCold, decimals=2)
    
    
    dataToSend = {
        "data" : dataWithLabel, 
        "collisionalBoltzmanPlotData" : {
            "collisionalData":{"x":energyKeys, "y":collisionalDistribution.tolist(), "name" : "collisional"},
            "boltzmanData":{"x":energyKeys, "y":boltzmanDistributionCold.tolist(), "name" : "boltzman"}
        },
        "differenceFromBoltzman": {"data": {"x":energyKeys, "y":differenceFromBoltzman.tolist(), "name":"Difference"}}
    }

    return sendData(dataToSend, calling_file=pt(__file__).stem)

def plot(simulateTime, simulateCounts):
    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)
    ax.plot(simulateTime.T*1e3, simulateCounts.T)
    ax.plot(simulateTime*1e3, simulateCounts.sum(axis=0), "k")
    ax.legend([*[f"J{i}" for i in energyKeys], "SUM"], title=f"He: {nHe:.2e}cm3")
    sourceTemp = 300
    trapTemp = 10
    ax.set(xlabel="Time (ms)", ylabel="Population (%)", title="Simulation: Thermal stabilisation by collision with $^4$He atoms "+f"({sourceTemp}K => {trapTemp}K)")
    plt.show()

rate_constants = None
nHe = None
boltzmanDistributionInitial = None
boltzmanDistributionCold = None
energyKeys = None


def main(args):

    global rate_constants, nHe, boltzmanDistributionInitial, energyKeys, boltzmanDistributionCold
    numberOfLevels = int(args["numberOfLevels"])
    print(f"{numberOfLevels=}", flush=True)
    rate_constants = {key: float(value) for key, value in args["collisionalRateConstantValues"].items()}
    nHe = float(args["numberDensity"])

    boltzmanDistribution = args["boltzmanDistributionValues"].values()
    
    boltzmanDistributionInitial = np.array(list(boltzmanDistribution)[:numberOfLevels], dtype=float)

    boltzmanDistributionCold = args["boltzmanDistributionColdValues"].values()
    boltzmanDistributionCold = np.array(list(boltzmanDistributionCold)[:numberOfLevels], dtype=float)
    energyKeys = args["energyKeys"][:numberOfLevels]
    print(f"{energyKeys=}", flush=True)
    simulate(args)

    