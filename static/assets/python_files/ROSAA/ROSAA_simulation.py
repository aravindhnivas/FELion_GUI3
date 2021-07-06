
import sys, json, pprint
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from functools import reduce

main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)
from FELion_definitions import sendData
from FELion_constants import colors

from ROSAA_func import boltzman_distribution

class ROSAA:


    def __init__(self):

        self.rate_coefficients = conditions["rate_coefficients"]
        self.simulation_parameters = conditions["simulation_parameters"]
        self.nHe = float(self.simulation_parameters["He density(cm3)"])

        self.energyLevels = {key : float(value) for key, value in conditions["energy_levels"].items()}
        self.energyKeys = list(self.energyLevels.keys())
        self.lineshape_conditions = conditions["lineshape_conditions"]
        self.collisionalTemp = float(self.lineshape_conditions["IonTemperature(K)"])
        
        self.collisionalRates = {key : float(value) for key, value in conditions["collisional_rates"].items()}

        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]

        self.includeCollision = conditions["includeCollision"]

        if self.includeSpontaneousEmission:
            self.einsteinA_Rates = {key : float(value) for key, value in conditions["einstein_coefficient"]["A"].items()}
            self.einsteinB_Rates = {key : float(value) for key, value in conditions["einstein_coefficient"]["B"].items()}

        self.Simulate()
        

    def SimulateODE(self, t, counts):
        
        if self.includeAttachmentRate:
            N = counts[:-self.totalAttachmentLevels]

            N_He = counts[-self.totalAttachmentLevels:]

        else: N = counts

        rateCollection = []
        N = {key:value for key, value in zip(self.energyKeys, N)}

        rateCollection = []
        for i in self.energyKeys:
            collisional = [0]

            einstein = [0]
            for j in self.energyKeys:
                if i!= j:
                    key = f"{j} --> {i}"
                    keyInverse = f"{i} --> {j}"

                    if self.includeCollision:
                        if key in self.collisionalRates and keyInverse in self.collisionalRates:

                            R_coll = self.collisionalRates[key]*N[j] - self.collisionalRates[keyInverse]*N[i]
                            collisional.append(R_coll)

                    
                    if self.includeSpontaneousEmission:
                        if key in self.einsteinA_Rates:

                            R_einsteinA = self.einsteinA_Rates[key]*N[j]
                            einstein.append(R_einsteinA)

                        if keyInverse in self.einsteinA_Rates:
                            R_einsteinA = -self.einsteinA_Rates[keyInverse]*N[i]
                            einstein.append(R_einsteinA)


                    if self.lightON:
                        if i in self.transitionLevels and j in self.transitionLevels:

                            R_einsteinB = self.einsteinB_Rates[key]*N[j] - self.einsteinB_Rates[keyInverse]*N[i]
                            einstein.append(R_einsteinB)

            collections = collisional + einstein
            rateCollection.append(collections)

        dR_dt = []

        for _ in rateCollection:
            temp = reduce(lambda a, b: a+b, _)

            dR_dt.append(temp)

        # return [*dR_dt, *N_He]

        return dR_dt
    
    def Simulate(self):

        duration = conditions["simulation_parameters"]["Simulation time(ms)"]
        duration = float(duration)*1e-3 # converting ms ==> s

        tspan = [0, duration]
        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]
        # energyUnit = conditions["energyUnit"]
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])
        self.boltzmanDistribution = boltzman_distribution(
            self.energyLevels, initialTemp, 
            self.electronSpin, self.zeemanSplit
        )

        self.totalAttachmentLevels = int(self.rate_coefficients["totalAttachmentLevels"])
        self.includeAttachmentRate = False # conditions["includeAttachmentRate"]

        N_He = []
        
        if self.includeAttachmentRate:
            N_He = self.totalAttachmentLevels*[0]

        totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulateTime = np.linspace(0, duration, totalSteps)

        self.lightON=False

        N_OFF = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], dense_output=True)
        self.lightOFF_distribution = N_OFF.sol(self.simulateTime)

        self.lightON=True
        self.excitedFrom = conditions["excitedFrom"]
        self.excitedTo = conditions["excitedTo"]
        self.transitionLevels = [self.excitedFrom, self.excitedTo]
        N_ON = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], dense_output=True)
        self.lightON_distribution = N_ON.sol(self.simulateTime)
        self.plot()

    def plot(self):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)

        simulationTime = self.simulateTime.T*1e3
        colorSchemes = []
        for color in colors[::2]:
            scale = 1/255
            temp = [_*scale for _ in color]
            colorSchemes.append(temp)
        
        self.molecule = conditions["main_parameters"]["molecule"]
        legends = [f"{self.molecule} ({key.strip()})" for key in self.energyKeys]

        counter = 0
        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):

            ax.plot(simulationTime, on, ls="-", c=colorSchemes[counter], label=f"{legends[counter]}")
            ax.plot(simulationTime, off, ls="--", c=colorSchemes[counter])
            counter += 1

        ax.plot(simulationTime, self.lightOFF_distribution.sum(axis=0), "--k")
        ax.plot(simulationTime, self.lightON_distribution.sum(axis=0), "-k", alpha=0.5)
        ax.legend(title=f"--OFF, -ON")
        ax.set(xlabel="Time (ms)", ylabel="Population (%)", title="Simulation", yscale="linear")

        pp.pprint(self.lightOFF_distribution.T[-1])
        sys.stdout.flush()
        plt.show()

if __name__ == "__main__":
    conditions = json.loads(sys.argv[1])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(conditions)

    sys.stdout.flush()
    ROSAA()