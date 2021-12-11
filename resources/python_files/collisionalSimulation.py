
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
    N = {key:value for key, value in zip(energyKeys, N)}
    rateCollection = []
    
    for i in energyKeys:
        collisional = []

        for j in energyKeys:
            if i!= j: 
                key = f"{j} --> {i}"
                keyInverse = f"{i} --> {j}"
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
        "collisionalBoltzmanPlotData" : {"collisionalData":{"x":energyKeys, "y":collisionalDistribution.tolist(), "name" : "collisional"}},
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

args = None
rate_constants, nHe, boltzmanDistributionInitial, energyKeys = None, None, None, None
def main(arguments):

    global args, rate_constants, nHe, boltzmanDistributionInitial, energyKeys
    args = arguments

    # args = sys.argv[1:][0].split(",")
    # args = json.loads(", ".join(args))
    print(args, flush=True)
    rate_constants = {key:float(value) for key, value in args["collisionalRateConstantValues"].items()}

    nHe = float(args["numberDensity"])
    
    boltzmanDistributionValues = args["boltzmanDistributionValues"]
    boltzmanDistributionInitial = list(boltzmanDistributionValues.values())
    boltzmanDistributionCold = args["boltzmanDistributionCold"]
    energyKeys = boltzmanDistributionCold["x"]
    boltzmanDistributionCold = np.array(boltzmanDistributionCold["y"], dtype=float)
    print(f"Received args: {args}, {type(args)}\n")

    simulate(args)