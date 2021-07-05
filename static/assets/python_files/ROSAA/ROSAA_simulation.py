
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
        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]
        energyUnit = conditions["energyUnit"]
        self.collisionalRateConstants = {key : float(value) for key, value in conditions["collisional_rates"].items()}

        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]

        self.includeCollision = conditions["includeCollision"]

        if self.includeSpontaneousEmission:
            self.einsteinA_rateConstants = {key : float(value) for key, value in conditions["einstein_coefficient"].items()}
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
                        if key in self.collisionalRateConstants and keyInverse in self.collisionalRateConstants:
                            R_coll = self.collisionalRateConstants[key]*self.nHe*N[j] - self.collisionalRateConstants[keyInverse]*self.nHe*N[i]
                            collisional.append(R_coll)

                    
                    if self.includeSpontaneousEmission:
                        if key in self.einsteinA_rateConstants:

                            R_einstein = self.einsteinA_rateConstants[key]*N[j]
                            einstein.append(R_einstein)

                        if keyInverse in self.einsteinA_rateConstants:
                            R_einstein = -self.einsteinA_rateConstants[keyInverse]*N[i]
                            einstein.append(R_einstein)
                            
                        # print(f"{einstein=}\n{collisional=}", flush=True)

            collections = collisional + einstein

            rateCollection.append(collisional)

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
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])
        self.boltzmanDistribution = boltzman_distribution(
            self.energyLevels, initialTemp, 
            self.electronSpin, self.zeemanSplit
        )

        self.totalAttachmentLevels = int(self.rate_coefficients["totalAttachmentLevels"])
        self.includeAttachmentRate = conditions["includeAttachmentRate"]

        N_He = []
        
        if self.includeAttachmentRate:
            N_He = self.totalAttachmentLevels*[0]

        N_OFF = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], dense_output=True)

        totalSteps = int(self.simulation_parameters["Total steps"])
        
        self.simulateTime = np.linspace(0, duration, totalSteps)
        
        self.lightOFF_distribution = N_OFF.sol(self.simulateTime)
        self.plot()

    def plot(self):
        fig, ax = plt.subplots(figsize=(7, 4), dpi=100)


        ax.plot(self.simulateTime.T*1e3, self.lightOFF_distribution.T)
        ax.plot(self.simulateTime*1e3, self.lightOFF_distribution.sum(axis=0), "k")
        ax.legend([*[f"J{i}" for i in self.energyKeys], "SUM"], title=f"He: {self.nHe:.2e}cm3")
        ax.set(xlabel="Time (ms)", ylabel="Population (%)", title="Simulation", yscale="linear")

        pp.pprint(self.lightOFF_distribution.T[-1])
        sys.stdout.flush()
        plt.show()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    conditions = json.loads(", ".join(args))

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(conditions)
    sys.stdout.flush()

    ROSAA()