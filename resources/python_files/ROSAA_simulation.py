
import json, pprint, time
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from functools import reduce

from ROSAA_func import boltzman_distribution
from optimizePlot import optimizePlot
from FELion_constants import pltColors
def log(msg): return print(msg, flush=True)

logCounter = 5
class ROSAA:

    def __init__(self):

        self.energyLevels = {key: float(value) for key, value in conditions["energy_levels"].items()}
        self.energyKeys = list(self.energyLevels.keys())
        self.lineshape_conditions = conditions["lineshape_conditions"]
        self.collisionalTemp = float(conditions["collisionalTemp"])
        
        self.collisionalRateConstants = {key: float(value) for key, value in conditions["collisional_rates"].items()}
        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]
        self.includeCollision = conditions["includeCollision"]
        if self.includeSpontaneousEmission:
            self.einsteinA_Rates = {key: float(value) for key, value in conditions["einstein_coefficient"]["A"].items()}
            self.einsteinB_Rates = {key: float(value) for key, value in conditions["einstein_coefficient"]["B"].items()}


        self.excitedFrom = str(conditions["excitedFrom"])
        self.excitedTo = str(conditions["excitedTo"])
        self.transitionLevels = [self.excitedFrom, self.excitedTo]

        self.start_time = time.perf_counter()
        variable = conditions["variable"]
        variableRange = conditions["variableRange"]
        self.writeFile = conditions["writefile"]
        
        if variable == "time":
            nHe = float(conditions["numberDensity"])

            self.molecule = conditions["main_parameters"]["molecule"]
            self.taggingPartner = conditions["main_parameters"]["tagging partner"]
            self.GetAttachmentRatesParameters()
            self.legends = [f"${self.molecule}$ ({key.strip()})" for key in self.energyKeys]
            if self.includeAttachmentRate:
                self.legends += [f"${self.molecule}${self.taggingPartner}"]
                self.legends += [f"${self.molecule}${self.taggingPartner}$_{i+1}$" for i in range(1, self.totalAttachmentLevels)]

            self.Simulate(nHe)

            self.Plot()
        
        elif variable == "He density(cm3)":

            signalList = []
            _start, _end, _steps = variableRange.split(",")

            dataList = np.linspace(float(_start), float(_end), int(_steps))
            for counter, _nHe in enumerate(dataList):
                log(f"{counter+1}/{int(_steps)}: {_nHe=:.2e}")

                self.Simulate(_nHe)

                if self.includeAttachmentRate:

                    signal_index = len(self.energyKeys)+1
                
                    signal = (1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:]))*100

                    signal = round(signal[-1], 1)
                    signalList.append(signal)
            
            signalList = np.nan_to_num(signalList).clip(min=0)
            
            log(signalList)

            location = pt(conditions["currentLocation"])/"OUT"
            if not location.exists():
                location.mkdir()

            savefilename = conditions["savefilename"]
            with open(location / f"{savefilename}_ROSAA_output_nHe_{_start}_{_end}_{int(_steps)}.dat", 'w+') as f:

                f.write("# nHe(cm-3)\tSignal(%)\n")

                for x, y in zip(dataList, signalList):
                    f.write(f"{x:.2e}\t{y:.2f}\n")
                log(f"{savefilename} file written in {location} folder.")

            
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            ax.plot(dataList, signalList, ".-")
            ax = optimizePlot(ax, xlabel="number Density ($cm^{-3}$)", ylabel="Signal (%)")
            ax.set_xscale("log")
            plt.show()

    def SimulateODE(self, t, counts, nHe):
        global logCounter
        
        if self.includeAttachmentRate and self.includeCollision:
            N = counts[:-self.totalAttachmentLevels]
            N_He = counts[-self.totalAttachmentLevels:]
        elif self.includeCollision: N = counts
        else: 
            N = self.N
            N_He = counts

        dR_dt = []
        # if self.includeCollision:

        N = {key: value for key, value in zip(self.energyKeys, N)}

        for i in self.energyKeys:

            einstein = []
            collisional = []

            for j in self.energyKeys:

                if i!= j:

                    key = f"{j} --> {i}"
                    keyInverse = f"{i} --> {j}"

                    if self.includeCollision:
                        if key in self.collisionalRateConstants and keyInverse in self.collisionalRateConstants:
                            R_coll = (self.collisionalRateConstants[key]*N[j] - self.collisionalRateConstants[keyInverse]*N[i])*nHe
                            collisional.append(R_coll)

                        if self.includeSpontaneousEmission:
                            if key in self.einsteinA_Rates:
                                R_einsteinA = self.einsteinA_Rates[key]*N[j]
                                einstein.append(R_einsteinA)

                            if keyInverse in self.einsteinA_Rates:
                                R_einsteinA = -self.einsteinA_Rates[keyInverse]*N[i]
                                einstein.append(R_einsteinA)

                    else:

                        ratio = np.copy(self.boltzmanDistributionCold)
                        self.N = (ratio/ratio.sum())*(1-np.sum(N_He))
                        self.N_distribution = np.append(self.N_distribution, self.N)
                        self.t_distribution = np.append(self.t_distribution, t)

                    if self.lightON:
                        if i in self.transitionLevels and j in self.transitionLevels:
                            R_einsteinB = self.einsteinB_Rates[key]*N[j] - self.einsteinB_Rates[keyInverse]*N[i]
                            einstein.append(R_einsteinB)

            collections = np.array(collisional + einstein).sum()

            if self.includeAttachmentRate:
                if i == self.excitedFrom:
                    attachmentRate0 = -(self.k3[0] * nHe**2 * N[i]) + (self.kCID[0] * nHe * N_He[0] * self.kCID_branch)
                    collections += attachmentRate0
                
                elif i == self.excitedTo:
                    attachmentRate1 =  -(self.k31_excited * nHe**2 *  N[j]) + (self.kCID[0] * nHe * N_He[0] * (1-self.kCID_branch))
                    collections += attachmentRate1

            dR_dt.append(collections)

        dRdt_N_He = []

        if self.includeAttachmentRate:
            currentRate = -(attachmentRate0 + attachmentRate1)

            for i in range(len(N_He)-1):
            
                nextRate = -(self.k3[i+1] * nHe**2 *N_He[i]) + (self.kCID[i+1] * nHe * N_He[i+1])

                attachmentRate = currentRate + nextRate
                dRdt_N_He.append(attachmentRate)

                if self.includeCollision: 
                    dR_dt.append(attachmentRate)

                currentRate = -nextRate

            dRdt_N_He.append(currentRate)
            if self.includeCollision: dR_dt.append(currentRate)

        if not self.includeCollision:
            return dRdt_N_He
        else:
            return dR_dt

    def GetAttachmentRatesParameters(self):

        self.attachment_rate_coefficients = conditions["attachment_rate_coefficients"]
        self.rateConstants = self.attachment_rate_coefficients["rateConstants"]

        self.k3 = [float(_) for _ in self.rateConstants["k3"]]
        self.k3_branch = float(self.attachment_rate_coefficients["a(k31)"])

        self.k31_excited = self.k3_branch*self.k3[0]
        
        self.kCID = [float(_) for _ in self.rateConstants["kCID"]]
        self.kCID_branch = float(self.attachment_rate_coefficients["branching-ratio(kCID)"])

        self.totalAttachmentLevels = int(self.attachment_rate_coefficients["totalAttachmentLevels"])
        self.includeAttachmentRate = conditions["includeAttachmentRate"]
    
    def Simulate(self, nHe):

        self.simulation_parameters = conditions["simulation_parameters"]
        
        duration = self.simulation_parameters["Simulation time(ms)"]
        duration = float(duration)*1e-3 # converting ms ==> s
        t0 = 0
        tspan = [t0, duration]

        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])

        self.boltzmanDistribution = boltzman_distribution( self.energyLevels, initialTemp, self.electronSpin, self.zeemanSplit )
        self.boltzmanDistributionCold = boltzman_distribution( self.energyLevels, self.collisionalTemp, self.electronSpin, self.zeemanSplit )
        
        
        N_He = []
        if self.includeAttachmentRate:
            N_He = self.totalAttachmentLevels*[0]
        
        totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulateTime = np.linspace(t0, duration, totalSteps)
        
        self.lightON=False
        
        start_time = time.perf_counter()
        N = self.boltzmanDistribution if self.includeCollision else []
        options = {
            "method": "Radau",
            "t_eval": self.simulateTime,
        }
        
        y_init = [*N, *N_He]

        # self.OFF_fixedPopulation = np.copy(self.boltzmanDistributionCold)
        # self.OFF_fixedPopulation_arr = [np.copy(self.boltzmanDistributionCold)]
        # self.OFF_fixedPopulation_arr_time = [0]
        
        # self.ON_fixedPopulation = np.copy(self.boltzmanDistributionCold)
        # self.ON_fixedPopulation_arr = [np.copy(self.boltzmanDistributionCold)]

        # self.ON_fixedPopulation_arr_time = [0]
        self.N = np.copy(self.boltzmanDistribution)
        self.N_distribution = np.array([])
        self.t_distribution = np.array([])
        N_OFF = solve_ivp(self.SimulateODE, tspan, y_init, args=(nHe, ), **options )

        log(f'{N_OFF.nfev=} evaluations required.')
        self.lightOFF_distribution = N_OFF.y
        N_OFF_distribution = {"t": self.t_distribution, "y": self.N_distribution}

        self.lightON=True
        self.N = np.copy(self.boltzmanDistribution)
        self.N_distribution = np.array([])
        self.t_distribution = np.array([])
        N_ON = solve_ivp(self.SimulateODE, tspan, y_init, args=(nHe, ), **options )
        self.lightON_distribution = N_ON.y
        log(f'{N_ON.nfev=} evaluations required.')
        N_ON_distribution = {"t": self.t_distribution, "y": self.N_distribution}

        dataToSend = {
            "legends":self.legends,
            "time (in s)":self.simulateTime.tolist(), 
            "lightON_distribution":self.lightON_distribution.tolist(),
            "lightOFF_distribution":self.lightOFF_distribution.tolist()

        }

        if self.writeFile: 
            self.WriteData("full", dataToSend)
        
        end_time = time.perf_counter()
        
        log(f"Current simulation time {(end_time - start_time):.2f} s")
        log(f"Total simulation time {(end_time - self.start_time):.2f} s")
        
    def Plot(self):
        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        simulationTime = self.simulateTime.T*1e3

        counter = 0
        if not self.includeCollision:
            

            self.ON_fixedPopulation_arr = np.array(self.ON_fixedPopulation_arr).T
            self.ON_fixedPopulation_arr_time = np.array(self.ON_fixedPopulation_arr_time)*1e3

            log(f"{self.ON_fixedPopulation_arr.T[-1].sum()=}")

            self.OFF_fixedPopulation_arr = np.array(self.OFF_fixedPopulation_arr).T
            self.OFF_fixedPopulation_arr_time = np.array(self.OFF_fixedPopulation_arr_time)*1e3

            for on, off in zip(self.ON_fixedPopulation_arr, self.OFF_fixedPopulation_arr):
                ax.plot(self.ON_fixedPopulation_arr_time, on, ls="-", c=pltColors[counter], label=f"{self.legends[counter]}")
                ax.plot(self.OFF_fixedPopulation_arr_time, off, ls="--", c=pltColors[counter])

                counter += 1

        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):
            ax.plot(simulationTime, on, ls="-", c=pltColors[counter], label=f"{self.legends[counter]}")
            ax.plot(simulationTime, off, ls="--", c=pltColors[counter])
            counter += 1

        ax.plot(simulationTime, self.lightON_distribution.sum(axis=0), "-k", alpha=0.5)
        ax.plot(simulationTime, self.lightOFF_distribution.sum(axis=0), "--k")
        
        ax.hlines(1, 0, simulationTime[-1]+simulationTime[-1]*0.2, colors='k', linestyles="dashdot")

        lg = ax.legend(title=f"--OFF, -ON", fontsize=14, title_fontsize=16)
        lg.set_draggable(True)
        ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Population")

        if self.includeAttachmentRate:

            signal_index = len(self.energyKeys)+1
            signal = (1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:]))*100

            signal = np.around(np.nan_to_num(signal).clip(min=0), 1)
            log(f"{signal=}")
            fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=100)

            ax1.plot(simulationTime[1:], signal, label=f"Signal: {signal[-1]} (%)")
            # ax1.plot(self.simulateTime_attachment[1:]*1e3, self.directSignal, label=f"Signal: {self.directSignal[-1]} (%)")
            ax1 = optimizePlot(ax1, xlabel="Time (ms)", ylabel="Signal (%)")
            # difference = signal[-1] - self.directSignal[-1]
            # log(f"{difference=}")
            ax1.legend()
        plt.show()

    def WriteData(self, name, dataToSend):
        location = pt(conditions["currentLocation"])

        savefilename = conditions["savefilename"]

        addText = ""
        if not self.includeAttachmentRate:
            addText = "_no-attachement"
        with open(location / f"OUT/{savefilename}{addText}_{name}_ROSAA_output.json", 'w+') as f:
            data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)
            log(f"{savefilename} file written in {location} folder.")

conditions = None
def main(arguments):
    global conditions
    conditions = arguments
    ROSAA()