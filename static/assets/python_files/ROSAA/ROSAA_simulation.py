
import sys, json, pprint, time
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
from optimizePlot import optimizePlot
class ROSAA:


    def __init__(self):

        
        

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


        self.excitedFrom = conditions["excitedFrom"]
        self.excitedTo = conditions["excitedTo"]
        self.transitionLevels = [self.excitedFrom, self.excitedTo]

        start_time = time.perf_counter()
        self.Simulate()
        end_time = time.perf_counter()
        print(f"Total simulation time {(end_time - start_time):.2f} s", flush=True)
        self.plot()

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

        if self.includeAttachmentRate:
            dR_dt = self.compute_attachment_process(N_He, dR_dt)
        
        # dR_dt = np.array(dR_dt, dtype=float)
        return dR_dt

    def compute_attachment_process(self, N_He, N):
        
        N = {key:value for key, value in zip(self.energyKeys, N)}
        attachmentRate0 = - self.k3[0]*N[self.excitedFrom] + self.kCID[0]*N_He[0]*self.kCID_branch
        attachmentRate1 = - self.k31_excited*N[self.excitedTo] + self.kCID[0]*N_He[0]*(1-self.kCID_branch)
        
        N[self.excitedFrom] += attachmentRate0
        N[self.excitedTo] += attachmentRate1
        dR_dt = list(N.values())
        # for the first complex formed (sign corrected)
        currentRate =  - attachmentRate0 - attachmentRate1

        for i in range(self.totalAttachmentLevels-1):
            nextRate = - self.k3[i+1]*N_He[i] + self.kCID[i+1]*N_He[i+1]
            attachmentRate = currentRate + nextRate
            dR_dt.append(attachmentRate)
            currentRate = -nextRate
        dR_dt.append(currentRate)
        return dR_dt

    def GetAttachmentRatesParameters(self):

        self.attachment_rate_coefficients = conditions["attachment_rate_coefficients"]
        self.rateConstants = self.attachment_rate_coefficients["rateConstants"]
        self.k3 = [float(_) for _ in self.rateConstants["k3"]]

        self.k3_branch = float(self.attachment_rate_coefficients["a(k31)"])
        self.k31_excited = self.k3_branch*self.k3[0]
        
        self.kCID  = [float(_) for _ in self.rateConstants["kCID"]]
        self.kCID_branch = float(self.attachment_rate_coefficients["branching-ratio(kCID)"])

        self.totalAttachmentLevels = int(self.attachment_rate_coefficients["totalAttachmentLevels"])
        self.includeAttachmentRate = conditions["includeAttachmentRate"]
    
    def Simulate(self):

        self.simulation_parameters = conditions["simulation_parameters"]
        
        duration = self.simulation_parameters["Simulation time(ms)"]
        duration = float(duration)*1e-3 # converting ms ==> s

        tspan = [0, duration]

        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]
        # energyUnit = conditions["energyUnit"]
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])

        self.boltzmanDistribution = boltzman_distribution( self.energyLevels, initialTemp, self.electronSpin, self.zeemanSplit )

        self.GetAttachmentRatesParameters()

        N_He = []
        if self.includeAttachmentRate:
        
            N_He = self.totalAttachmentLevels*[0]
            print(f"{N_He=}", flush=True)

        totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulateTime = np.linspace(0, duration, totalSteps)
        self.lightON=False

        N_OFF = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], dense_output=True)

        self.lightOFF_distribution = N_OFF.sol(self.simulateTime)
        self.lightON=True

        
        N_ON = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], dense_output=True)
        self.lightON_distribution = N_ON.sol(self.simulateTime)
        

    def plot(self):

        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        # plt.subplots_adjust(top=0.95, right=0.95, left=0.07)
        simulationTime = self.simulateTime.T*1e3
        colorSchemes = []
        for color in colors[::2]:
            scale = 1/255
            temp = [_*scale for _ in color]
            colorSchemes.append(temp)
        
        self.molecule = conditions["main_parameters"]["molecule"]
        self.taggingPartner = conditions["main_parameters"]["tagging partner"]
        legends = [f"${self.molecule}$ ({key.strip()})" for key in self.energyKeys]


        if self.includeAttachmentRate:
            legends += [f"${self.molecule}${self.taggingPartner}"]
            legends += [f"${self.molecule}${self.taggingPartner}$_{i+1}$" for i in range(1, self.totalAttachmentLevels)]
        counter = 0
        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):

            ax.plot(simulationTime, on, ls="-", c=colorSchemes[counter], label=f"{legends[counter]}")
            ax.plot(simulationTime, off, ls="--", c=colorSchemes[counter])
            counter += 1
        ax.plot(simulationTime, self.lightOFF_distribution.sum(axis=0), "--k")
        ax.plot(simulationTime, self.lightON_distribution.sum(axis=0), "-k", alpha=0.5)
        
        ax.hlines(1, 0, simulationTime[-1]+simulationTime[-1]*0.2, colors='k', linestyles="dashdot")

        lg = ax.legend(title=f"--OFF, -ON", fontsize=14, title_fontsize=16)
        
        lg.set_draggable(True)
        ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Population (%)")

        signal_index = len(self.energyKeys)+1
        signal = (1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:]))*100

        fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
        ax1.plot(simulationTime[1:], signal)
        ax1 = optimizePlot(ax1, xlabel="Time (ms)", ylabel="Signal (%)")

        plt.show()

if __name__ == "__main__":
    conditions = json.loads(sys.argv[1])

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(conditions)
    sys.stdout.flush()

    ROSAA()