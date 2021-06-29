
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
    
    global _rateCollection
    N = {key:value for key, value in zip(energyKeys, N)}
    _N = [f"N{i}" for i in range(len(energyKeys))]

    _N = {key:value for key, value in zip(energyKeys, _N)}
    
    
    _rateCollection = []
    rateCollection = []
    
    for i in energyKeys:
        _collisional = []
        collisional = []

        for j in energyKeys:
            if i!= j: 
                key = f"{j} --> {i}"
                keyInverse = f"{i} --> {j}"
                _k = f" + q({key})*{_N[j]} - q({keyInverse})*{_N[i]}"
                _collisional.append(_k)
                
                k = rate_constants[key]*nHe*N[j] - rate_constants[keyInverse]*nHe*N[i]
                collisional.append(k)

                
        _rateCollection.append(_collisional)
        rateCollection.append(collisional)
    
    dR_dt = []


    for _ in rateCollection:
        temp = reduce(lambda a, b: a+b, _)
        dR_dt.append(temp)
    
    return dR_dt

def simulate(args):

    time = float(args["duration"])*1e-3

    tspan = [0, time]
    
    N_collisional = solve_ivp(collisionalRateDistribution, tspan, boltzmanDistribution, dense_output=True)
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
    
    collisionalBoltzmanPlotData = {"data":{"x":energyKeys, "y":simulateCounts.T[-1].tolist()}}


    # colorIndex = 0
    # boltzmanDistributionCold = {}
    # for level, population in boltzmanDistributionValues:
        
    #     lineColor = {"color": f"rgb{colors[colorIndex]}"}

    #     style = {"fill": 'none'}
    #     boltzmanDistributionCold[level] = {"x":level, "y":population, "name":level, **defaultStyle, **style, **lineColor} 

    #     colorIndex += 2
    
    dataToSend = {
        "data" : dataWithLabel, 
        "collisionalBoltzmanPlotData" : collisionalBoltzmanPlotData,
        # "boltzmanDistributionCold" : boltzmanDistributionCold
    }

    # plot(simulateTime, simulateCounts)

    return sendData(dataToSend)


def plot(simulateTime, simulateCounts):

    fig, ax = plt.subplots(figsize=(7, 4), dpi=100)

    ax.plot(simulateTime.T*1e3, simulateCounts.T)

    ax.plot(simulateTime*1e3, simulateCounts.sum(axis=0), "k")
    ax.legend([*[f"J{i}" for i in energyKeys], "SUM"], title=f"He: {nHe:.2e}cm3")

    sourceTemp = 300
    trapTemp = 10
    ax.set(xlabel="Time (ms)", ylabel="Population (%)", title="Simulation: Thermal stabilisation by collision with $^4$He atoms "+f"({sourceTemp}K => {trapTemp}K)")

    plt.show()


if __name__ == "__main__":

    _rateCollection = []

    args = sys.argv[1:][0].split(",")

    args = json.loads(", ".join(args))
    print(args, flush=True)
    rate_constants = {key:float(value) for key, value in args["collisionalRateConstantValues"].items()}

    nHe = float(args["numberDensity"])
    boltzmanDistributionValues = args["boltzmanDistributionValues"]

    energyKeys = list(boltzmanDistributionValues.keys())
    boltzmanDistribution = list(boltzmanDistributionValues.values())

    print(f"Received args: {args}, {type(args)}\n")
    
    print(f"{rate_constants=}\n")
    simulate(args)

    # print(_rateCollection)
    _dR_dt = []

    for _ in _rateCollection:
        _temp = reduce(lambda a, b: a+b, _)
        _dR_dt.append(_temp)
    print("\n", _dR_dt)