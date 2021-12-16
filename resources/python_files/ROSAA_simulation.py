
import sys, json, pprint, time, os
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from functools import reduce

from ROSAA_func import boltzman_distribution
from optimizePlot import optimizePlot
from FELion_constants import pltColors
def log(msg): return print(msg, flush=True)


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
            
            # if self.writeFile:
                # self.WriteData()
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
                os.mkdir(location)

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

    def SimulateODESeparate(self, nHe, duration, totalSteps=1000, initialDuration=0.1):

        self.N_distribution = []
        self.t_distribution = []

        self.N = None
        def SimulateODEAttachment(t, N_He, ratio):
            if self.N is None:
                self.N = ratio
            self.N = (ratio/ratio.sum())*(1-np.sum(N_He))
            self.N_distribution = np.append(self.N_distribution, self.N)
            self.t_distribution = np.append(self.t_distribution, t)
            N = {key: value for key, value in zip(self.energyKeys, self.N)}

            attachmentRate0 = - self.k3[0] * nHe**2 * N[self.excitedFrom] + \
                self.kCID[0] * nHe * N_He[0] * self.kCID_branch
            attachmentRate1 = - self.k31_excited * nHe**2 * N[self.excitedTo] + \
                self.kCID[0] * nHe * N_He[0] * (1-self.kCID_branch)

            N[self.excitedFrom] += attachmentRate0
            N[self.excitedTo] += attachmentRate1
            # self.N = np.array(list(N.values()), dtype=float)

            dR_dt = []

            currentRate =  - attachmentRate0 - attachmentRate1
            for i in range(self.totalAttachmentLevels-1):
                nextRate = - self.k3[i+1] * nHe**2 * N_He[i] + self.kCID[i+1] * nHe * N_He[i+1]
                attachmentRate = currentRate + nextRate
                dR_dt.append(attachmentRate)
                currentRate = -nextRate
            dR_dt.append(currentRate)
            dR_dt = np.array(dR_dt, dtype=float)

            if self.includeAttachmentRate:
                return dR_dt
            else:
                return [0, 0]

        def SimulateODECollisional(t, N, lightON):

            N = {key: value for key, value in zip(self.energyKeys, N)}

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

        def simulatedFixedCollisional(lightON=True):
            N = {key: value for key, value in zip(self.energyKeys, self.boltzmanDistributionCold)}

            if lightON:

                if not self.zeemanSplit:
                
                    if self.electronSpin:
                
                        j0 = float(self.excitedFrom.split("_")[1])
                        j1 = float(self.excitedTo.split("_")[1])

                    else:
                        j0 = int(self.excitedFrom)
                        j1 = int(self.excitedTo)
                    G0 = int(2*j0+1)
                    G1 = int(2*j1+1)

                else:
                    G0 = G1 = 1

                twoLeveltotal = N[self.excitedFrom] + N[self.excitedTo]
                log(f"{twoLeveltotal=}")
                
                norm = G0 + G1
                N[self.excitedFrom] = (G0/norm)*twoLeveltotal
                N[self.excitedTo] = (G1/norm)*twoLeveltotal
                log(f"{N=}")
            converted_N = np.array(list(N.values()), dtype=float)
            return converted_N

        def plot():
            fig, ax = plt.subplots(figsize=(10, 6), dpi=100)

            counter = 0
            simulationTimeON = N_ON_distribution["t"]*1e3
            simulationTimeOFF = N_OFF_distribution["t"]*1e3
            
            for on, off in zip(N_ON_distribution["y"], N_OFF_distribution["y"]):
                ax.plot(simulationTimeON, on, ls="-", c=pltColors[counter], label=f"{self.legends[counter]}")
                ax.plot(simulationTimeOFF, off, ls="--", c=pltColors[counter])
                counter += 1

            ax.hlines(1, 0, simulationTimeON[-1]+simulationTimeON[-1]*0.2, colors='k', linestyles="dashdot")
            lg = ax.legend(title=f"--OFF, -ON", fontsize=14, title_fontsize=16)
            lg.set_draggable(True)

            # tagCounter = 1
            if self.includeAttachmentRate:
                for on, off in zip(N_He_ON_distribution, N_He_OFF_distribution):

                    ax.plot(self.simulateTime_attachment*1e3, on, ls="-", c=pltColors[counter], label=f"{self.legends[counter]}")
                    ax.plot(self.simulateTime_attachment*1e3, off, ls="--", c=pltColors[counter])
                    # tagCounter += 1
                    counter += 1
            
            ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Population (%)")
            if self.includeAttachmentRate:
                fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
                signalTime = self.simulateTime_attachment*1e3
                ax1.set_ylim([0, 100])
                ax1.plot(signalTime[1:], signal, label=f"Signal={signal[-1]:.0f}%")
                ax1 = optimizePlot(ax1, xlabel="Time (ms)", ylabel="Signal (%)")


                ax1.legend()
            plt.show(block = False)

        simulateTime_collisional = np.linspace(0, initialDuration, int(totalSteps))
        
        self.simulateTime_attachment = np.linspace(initialDuration, duration, int(totalSteps))
        start_time = time.perf_counter()
        ########################################################################################
        # Light OFF
        self.N_distribution = []
        self.t_distribution = []

        self.N = None

        if self.includeCollision:

            # Compute collisional
            N_OFF_collisional = solve_ivp(
                SimulateODECollisional, [0, initialDuration], self.boltzmanDistribution, args=(False, ), dense_output=True
            )

            ratio = N_OFF_collisional.sol(simulateTime_collisional).T[-1]
        else:

            ratio = self.boltzmanDistributionCold
        log(f"OFF: {ratio=}")
        # Compute attachment
        N_OFF_attachment = solve_ivp(
            SimulateODEAttachment, [initialDuration, duration], [0, 0], args=(ratio, ), dense_output=True
        )

        N_He_OFF_distribution = N_OFF_attachment.sol(self.simulateTime_attachment)

        shape = (len(self.t_distribution), len(self.boltzmanDistribution))
        self.N_distribution = np.array(self.N_distribution, dtype=float).reshape(shape).T
        # log(f"OFF: {np.around(self.N_distribution, 4)}")
        N_OFF_distribution = {"t": self.t_distribution, "y": self.N_distribution}

        ########################################################################################
        # Light ON
        self.N_distribution = []
        self.t_distribution = []
        self.N = None
        if self.includeCollision:
            N_ON_collisional = solve_ivp(
                SimulateODECollisional, [0, initialDuration], self.boltzmanDistribution, args=(True, ), dense_output=True
            )

            ratio = N_ON_collisional.sol(simulateTime_collisional).T[-1]
        else:
            ratio = simulatedFixedCollisional()
        log(f"ON: {ratio=}")
        # Compute attachment
        N_ON_attachment = solve_ivp(
            SimulateODEAttachment, [initialDuration, duration], [0, 0], args=(ratio, ), dense_output=True
        )

        N_He_ON_distribution = N_ON_attachment.sol(self.simulateTime_attachment)
        shape = (len(self.t_distribution), len(self.boltzmanDistribution))
        self.N_distribution = np.array(self.N_distribution, dtype=float).reshape(shape).T

        N_ON_distribution = {"t": self.t_distribution, "y": self.N_distribution}

        # log(f"ON: {np.around(self.N_distribution, 4)}")
        ########################################################################################
        ########################################################################################

        end_time = time.perf_counter()
        if self.includeAttachmentRate:
            log(f"Total simulation time: {(end_time-start_time):.2f} s")
            signal = (1 - (N_He_ON_distribution[1][1:] / N_He_OFF_distribution[1][1:]))*100
            signal = np.around(np.nan_to_num(signal).clip(min=0), 0)
            log(f"{signal=}")
            self.directSignal = signal

        else:
            signal = np.array([0])

        dataToSend = {
            "legends" : self.legends,
            "N_ON_distribution" : {"t": N_ON_distribution["t"].tolist(), "y": N_ON_distribution["y"].tolist()},
            "N_OFF_distribution" : {"t": N_OFF_distribution["t"].tolist(), "y": N_OFF_distribution["y"].tolist()},
            "N_He_ON_distribution" : N_He_ON_distribution.tolist(),
            "N_He_OFF_distribution" : N_He_OFF_distribution.tolist(),
            "simulateTime_attachment" : self.simulateTime_attachment.tolist(),
            "signal": signal.tolist()
        }
        if self.writeFile: self.WriteData("separate", dataToSend)
        plot()

        
    def compute_attachment_process(self, N_He, N, nHe):
        N = {key:value for key, value in zip(self.energyKeys, N)}

        attachmentRate0 = - self.k3[0]*nHe**2*N[self.excitedFrom] + self.kCID[0]*nHe*N_He[0]*self.kCID_branch
        attachmentRate1 = - self.k31_excited*nHe**2*N[self.excitedTo] + self.kCID[0]*nHe*N_He[0]*(1-self.kCID_branch)


        N[self.excitedFrom] += attachmentRate0
        N[self.excitedTo] += attachmentRate1
        dR_dt = list(N.values())


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
        
        # self.GetAttachmentRatesParameters()

        N_He = []
        if self.includeAttachmentRate:
            N_He = self.totalAttachmentLevels*[0]

        totalSteps = int(self.simulation_parameters["Total steps"])

        self.SimulateODESeparate(nHe, duration, totalSteps)
        if not self.includeCollision: return

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
        dataToSend = {
            "legends":self.legends,
            "time (in s)":self.simulateTime.tolist(), 
            "lightON_distribution":self.lightON_distribution.tolist(),
            "lightOFF_distribution":self.lightOFF_distribution.tolist()
        }
        if self.writeFile: self.WriteData("full", dataToSend)
        end_time = time.perf_counter()
        log(f"Current simulation time {(end_time - start_time):.2f} s")
        log(f"Total simulation time {(end_time - self.start_time):.2f} s")
        
    def Plot(self):

        fig, ax = plt.subplots(figsize=(10, 6), dpi=100)
        simulationTime = self.simulateTime.T*1e3
        counter = 0
        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):
            ax.plot(simulationTime, on, ls="-", c=pltColors[counter], label=f"{self.legends[counter]}")
            ax.plot(simulationTime, off, ls="--", c=pltColors[counter])
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
            signal = np.around(np.nan_to_num(signal).clip(min=0), 1)
            log(f"{signal=}")
            fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
            ax1.plot(simulationTime[1:], signal, label=f"Signal: {signal[-1]} (%)")
            ax1.plot(self.simulateTime_attachment[1:]*1e3, self.directSignal, label=f"Signal: {self.directSignal[-1]} (%)")

            ax1 = optimizePlot(ax1, xlabel="Time (ms)", ylabel="Signal (%)")

            difference = signal[-1] - self.directSignal[-1]
            log(f"{difference=}")
            ax1.legend()
        plt.show(block=True)

    def WriteData(self, name, dataToSend):

        location = pt(conditions["currentLocation"])

        savefilename = conditions["savefilename"]

        addText = ""
        if not self.includeAttachmentRate:
            addText = "_no-attachement"

        with open(location / f"{savefilename}{addText}_{name}_ROSAA_output.json", 'w+') as f:
            data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)

            log(f"{savefilename} file written in {location} folder.")


conditions = None
def main(arguments):
    global conditions
    conditions = arguments

    # conditions = json.loads(sys.argv[1])
    
    pp = pprint.PrettyPrinter(indent=4)
    
    pp.pprint(conditions)
    ROSAA()