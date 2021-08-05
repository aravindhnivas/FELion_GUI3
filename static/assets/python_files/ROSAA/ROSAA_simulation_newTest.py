
import sys, json, pprint, time, os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from functools import reduce

from ROSAA_func import boltzman_distribution
from optimizePlot import optimizePlot
main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)

from FELion_definitions import sendData
from FELion_constants import colors


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


        self.excitedFrom = conditions["excitedFrom"]
        self.excitedTo = conditions["excitedTo"]
        self.transitionLevels = [self.excitedFrom, self.excitedTo]

        self.start_time = time.perf_counter()
        variable = conditions["variable"]
        variableRange = conditions["variableRange"]

        
        if variable == "time":

            nHe = float(conditions["numberDensity"])
            self.Simulate(nHe)
            

            self.molecule = conditions["main_parameters"]["molecule"]
            self.taggingPartner = conditions["main_parameters"]["tagging partner"]

            self.legends = [f"${self.molecule}$ ({key.strip()})" for key in self.energyKeys]
            if self.includeAttachmentRate:
                self.legends += [f"${self.molecule}${self.taggingPartner}"]
                self.legends += [f"${self.molecule}${self.taggingPartner}$_{i+1}$" for i in range(1, self.totalAttachmentLevels)]
            self.writeFile = conditions["writefile"]
            
            if self.writeFile:
                self.WriteData()
            self.Plot()
        
        elif variable == "He density(cm3)":
            signalList = []
            _start, _end, _steps = variableRange.split(",")

            dataList = np.linspace(float(_start), float(_end), int(_steps))
            for counter, _nHe in enumerate(dataList):
                print(f"{counter+1}/{int(_steps)}: {_nHe=:.2e}", flush=True)

                self.Simulate(_nHe)
                
                if self.includeAttachmentRate:
                    signal_index = len(self.energyKeys)+1
                
                    signal = (1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:]))*100

                    signal = round(signal[-1], 1)
                    signalList.append(signal)

            
            signalList = np.nan_to_num(signalList).clip(min=0)
            print(signalList, flush=True)

            location = pt(conditions["currentLocation"])/"OUT"
            if not location.exists():
                os.mkdir(location)

            savefilename = conditions["savefilename"]
            with open(location / f"{savefilename}_ROSAA_output_nHe_{_start}_{_end}_{int(_steps)}.dat", 'w+') as f:

                f.write("# nHe(cm-3)\tSignal(%)\n")

                for x, y in zip(dataList, signalList):
                    f.write(f"{x:.2e}\t{y:.2f}\n")
                print(f"{savefilename} file written in {location} folder.", flush=True)
            
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
            ax.plot(dataList, signalList, ".-")
            ax = optimizePlot(ax, xlabel="number Density ($cm^{-3}$)", ylabel="Signal (%)")
            ax.set_xscale("log")

            plt.show()

    def SimulateODE(self, t, counts, nHe):
        
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
                            R_coll = (self.collisionalRateConstants[key]*N[j] - self.collisionalRateConstants[keyInverse]*N[i])*nHe
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
            dR_dt = self.compute_attachment_process(N_He, dR_dt, nHe)

        return dR_dt

    def SimulateODESeparate(self, nHe, duration, initialDuration=0.1, totalSteps=1000):

        self.Noff = []
        def SimulateODEAttachment(self, t, N_He, ratio, nHe):
            self.N = (ratio/ratio.sum())*self.N.sum()
            self.Noff = np.append(self.Noff, self.N)

            self.N = {key:value for key, value in zip(self.energyKeys, self.N)}
            attachmentRate0 = - self.k3[0]*nHe**2*self.N[self.excitedFrom] + self.kCID[0]*nHe*N_He[0]*self.kCID_branch

            attachmentRate1 = - self.k31_excited*nHe**2*self.N[self.excitedTo] + self.kCID[0]*nHe*N_He[0]*(1-self.kCID_branch)
            
            self.N[self.excitedFrom] += attachmentRate0
            self.N[self.excitedTo] += attachmentRate1
            dR_dt = list(self.N.values())

            # for the first complex formed (sign corrected)
            currentRate =  - attachmentRate0 - attachmentRate1

            for i in range(self.totalAttachmentLevels-1):
                nextRate = - self.k3[i+1]*nHe**2*N_He[i] + self.kCID[i+1]*nHe*N_He[i+1]
                attachmentRate = currentRate + nextRate
                dR_dt.append(attachmentRate)
                currentRate = -nextRate
            
            
            dR_dt.append(currentRate)
            return N_He

        def SimulateODECollisional(t, N, nHe, lightON):
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
                                R_coll = (self.collisionalRateConstants[key]*N[j] - self.collisionalRateConstants[keyInverse]*N[i])*nHe
                                collisional.append(R_coll)

                        if self.includeSpontaneousEmission:
                            if key in self.einsteinA_Rates:
                                R_einsteinA = self.einsteinA_Rates[key]*N[j]
                                einstein.append(R_einsteinA)

                            if keyInverse in self.einsteinA_Rates:
                                R_einsteinA = -self.einsteinA_Rates[keyInverse]*N[i]
                                einstein.append(R_einsteinA)

                        if lightON:
                            if i in self.transitionLevels and j in self.transitionLevels:
                                R_einsteinB = self.einsteinB_Rates[key]*N[j] - self.einsteinB_Rates[keyInverse]*N[i]
                                einstein.append(R_einsteinB)

                collections = collisional + einstein
                rateCollection.append(collections)


            dR_dt = []
            for _ in rateCollection:
                temp = reduce(lambda a, b: a+b, _)
                dR_dt.append(temp)

            return dR_dt

        simulateTime_collisional = np.linspace(0, initialDuration, int(totalSteps))
        simulateTime_attachment = np.linspace(initialDuration, duration, int(totalSteps))

        start_time = time.perf_counter()
        N_OFF_collisional = solve_ivp(SimulateODECollisional, [0, initialDuration], self.boltzmanDistribution, args=(nHe, False), dense_output=True)
        self.N = N_OFF_collisional.sol(simulateTime_collisional).T[-1]
        N_OFF_attachment = solve_ivp(SimulateODEAttachment, [initialDuration, duration], [0, 0], args=(self.N, nHe), dense_output=True)
        lightOFF_distribution = N_OFF_attachment.sol(simulateTime_attachment)

        end_time = time.perf_counter()


        
    def compute_attachment_process(self, N_He, N, nHe):
        
        N = {key:value for key, value in zip(self.energyKeys, N)}
        attachmentRate0 = - self.k3[0]*nHe**2*N[self.excitedFrom] + self.kCID[0]*nHe*N_He[0]*self.kCID_branch
        attachmentRate1 = - self.k31_excited*nHe**2*N[self.excitedTo] + self.kCID[0]*nHe*N_He[0]*(1-self.kCID_branch)
        
        
        N[self.excitedFrom] += attachmentRate0
        N[self.excitedTo] += attachmentRate1
        dR_dt = list(N.values())

        # for the first complex formed (sign corrected)
        
        currentRate =  - attachmentRate0 - attachmentRate1

        for i in range(self.totalAttachmentLevels-1):
            nextRate = - self.k3[i+1]*nHe**2*N_He[i] + self.kCID[i+1]*nHe*N_He[i+1]
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
        
        self.kCID = [float(_) for _ in self.rateConstants["kCID"]]
        self.kCID_branch = float(self.attachment_rate_coefficients["branching-ratio(kCID)"])

        self.totalAttachmentLevels = int(self.attachment_rate_coefficients["totalAttachmentLevels"])
        self.includeAttachmentRate = conditions["includeAttachmentRate"]
    
    def Simulate(self, nHe):

        self.simulation_parameters = conditions["simulation_parameters"]
        duration = self.simulation_parameters["Simulation time(ms)"]
        duration = float(duration)*1e-3 # converting ms ==> s

        tspan = [0, duration]

        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])
        self.boltzmanDistribution = boltzman_distribution( self.energyLevels, initialTemp, self.electronSpin, self.zeemanSplit )
        self.boltzmanDistributionCold = boltzman_distribution( self.energyLevels, self.collisionalTemp, self.electronSpin, self.zeemanSplit )

        self.fixedPopulation = boltzman_distribution( self.energyLevels, self.collisionalTemp, self.electronSpin, self.zeemanSplit )
        self.GetAttachmentRatesParameters()
        N_He = []

        if self.includeAttachmentRate:
        
            N_He = self.totalAttachmentLevels*[0]
            # print(f"{N_He=}", flush=True)

        totalSteps = int(self.simulation_parameters["Total steps"])
        initialDuration = 5e-3

        initialSteps = np.linspace(0, initialDuration, int(totalSteps*0.5))
        finalSteps = np.linspace(initialDuration, duration, int(totalSteps*0.5))
        if duration>initialDuration:
            self.simulateTime = np.append(initialSteps, finalSteps)
        else:
            self.simulateTime = np.linspace(0, duration, int(totalSteps*0.5))

        self.lightON=False
        start_time = time.perf_counter()
        N_OFF = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], args=(nHe,), dense_output=True)
        self.lightOFF_distribution = N_OFF.sol(self.simulateTime)
        self.lightON=True

        N_ON = solve_ivp(self.SimulateODE, tspan, [*self.boltzmanDistribution, *N_He], args=(nHe, ), dense_output=True)
        
        self.lightON_distribution = N_ON.sol(self.simulateTime)

        end_time = time.perf_counter()
        print(f"Current simulation time {(end_time - start_time):.2f} s", flush=True)
        print(f"Total simulation time {(end_time - self.start_time):.2f} s", flush=True)
        
    def Plot(self):

        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        # plt.subplots_adjust(top=0.95, right=0.95, left=0.07)
        simulationTime = self.simulateTime.T*1e3
        colorSchemes = []
        for color in colors[::2]:
            scale = 1/255
            temp = [_*scale for _ in color]
            colorSchemes.append(temp)
        
        counter = 0
        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):
            ax.plot(simulationTime, on, ls="-", c=colorSchemes[counter], label=f"{self.legends[counter]}")
            ax.plot(simulationTime, off, ls="--", c=colorSchemes[counter])
            counter += 1

        ax.plot(simulationTime, self.lightOFF_distribution.sum(axis=0), "--k")
        ax.plot(simulationTime, self.lightON_distribution.sum(axis=0), "-k", alpha=0.5)
        
        ax.hlines(1, 0, simulationTime[-1]+simulationTime[-1]*0.2, colors='k', linestyles="dashdot")

        lg = ax.legend(title=f"--OFF, -ON", fontsize=14, title_fontsize=16)
        lg.set_draggable(True)
        ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Population (%)")

        if self.includeAttachmentRate:
            signal_index = len(self.energyKeys)+1

            signal = (1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:]))*100
            fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
            ax1.plot(simulationTime[1:], signal)
            ax1 = optimizePlot(ax1, xlabel="Time (ms)", ylabel="Signal (%)")
        plt.show()

    def WriteData(self):
        location = pt(conditions["currentLocation"])

        savefilename = conditions["savefilename"]
        dataToSend = {
            "legends":self.legends,
            "time (in s)":self.simulateTime.tolist(), 
            "lightON_distribution":self.lightON_distribution.tolist(),
            "lightOFF_distribution":self.lightOFF_distribution.tolist()
        }


        with open(location / f"{savefilename}_ROSAA_output.json", 'w+') as f:
            data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)

            print(f"{savefilename} file written in {location} folder.", flush=True)

if __name__ == "__main__":
    conditions = json.loads(sys.argv[1])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(conditions)
    sys.stdout.flush()
    ROSAA()