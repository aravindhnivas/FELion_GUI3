
import sys, json
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import speed_of_light, Boltzmann, Planck
from functools import reduce
from scipy.integrate import solve_ivp

from pathlib import Path as pt
from ROSAA_func import distribution, boltzman_distribution, \
    stimulated_absorption, stimulated_emission,\
    voigt, lorrentz_fwhm, gauss_fwhm

class ROSAA():

    def __init__(self, conditions):

        self.conditions = conditions


        self.save_parameters_to_file()
        self.deconstruct_parameters()
        self.get_collisional_rates()
        self.begin_simulation()

    def save_parameters_to_file(self):
        self.currentLocation = self.conditions["currentLocation"]
        self.filename = self.conditions["filename"]
        self.writefile = conditions["writefile"]
        with open(pt(self.currentLocation) / f"{self.filename}.json", 'w+') as f:
            data = json.dumps(self.conditions, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)

    def deconstruct_parameters(self):
        self.main_parameters = self.conditions["main_parameters"]
        self.simulation_parameters = self.conditions["simulation_parameters"]
        self.einstein_coefficient = self.conditions["einstein_coefficient"]
        self.lineshape_conditions = self.conditions["lineshape_conditions"]
        self.rate_coefficients = self.conditions["rate_coefficients"]
        self.power_broadening = self.conditions["power_broadening"]

        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]
        self.includeCollision = conditions["includeCollision"]
        self.includeAttachmentRate = conditions["includeAttachmentRate"]

        self.totallevel = int(conditions["numberOfLevels"])
        self.totalAttachmentLevels = int(self.rate_coefficients["totalAttachmentLevels"])

        self.Energy = [float(_) for _ in self.main_parameters["Energy"].split(", ")]
        self.trapTemp = float(self.conditions["trapTemp"])
        self.excitedTo = self.simulation_parameters["excitedTo"]
        self.excitedFrom = self.simulation_parameters["excitedFrom"]
        self.freq = float(self.main_parameters["freq"])
        
        self.molecule = self.main_parameters["molecule"]
        self.taggingPartner = self.main_parameters["tagging partner"]

    def get_collisional_rates(self):

        collisional_rates = {q:float(value) for q, value in self.conditions["collisional_rates"].items()}
        q_deexcitation_mode = self.conditions["deexcitation"]
        rates = {}
        for i in range(self.totallevel):
            for j in range(self.totallevel):

                if i != j & j>i:
                
                    deexciteRateConstantKey = f"q_{j}{i}"
                    exciteRateConstantKey = f"q_{i}{j}"
                    
                    if q_deexcitation_mode:
                        
                        _temp = collisional_rates[deexciteRateConstantKey]
                
                        rates[deexciteRateConstantKey] = _temp
                        rates[exciteRateConstantKey] = _temp * distribution(i, j, self.Energy, self.trapTemp)
                        
                    else:
                        _temp = collisional_rates[exciteRateConstantKey]
                        rates[exciteRateConstantKey] = _temp

                        rates[deexciteRateConstantKey] = _temp * distribution(j, i, self.Energy, self.trapTemp)

        self.collisional_rates = rates

    def compute_collision_process(self, i, N):
    
        collections = []

        for j in range(self.totallevel):
            if i!= j: 
                
                key = f"q_{j}{i}"
                keyInverse = f"q_{i}{j}"
                
                k = self.collisional_rates[key]*self.nHe*N[j] - self.collisional_rates[keyInverse]*self.nHe*N[i]
                collections.append(k)
        
        return collections
    
    def compute_einstein_process(self, i, N):
        collections = []
        
        if self.includeSpontaneousEmission:

            # Einstein Coefficient A
            if i == self.excitedFrom: 
                temp = self.A_10*N[self.excitedTo]
                collections.append(temp)

            if i == self.excitedTo:
                temp = -self.A_10*N[self.excitedTo]
                collections.append(temp)

        # Einstein Coefficient B

        if self.lightON:
            
            # B_rate defined from excited state 
            B_rate = self.B_01*N[self.excitedFrom] - self.B_10*N[self.excitedTo]

            if i == self.excitedFrom:
                temp = -B_rate
                collections.append(temp)

            if i == self.excitedTo:
                temp = B_rate
                collections.append(temp)
        return collections

    def compute_attachment_process(self, N, N_He, dR_dt):
    
        attachmentRate0 = - self.Rate_K3[0]*N[0] + self.Rate_kCID[0]*N_He[0]*self.p
        attachmentRate1 = - self.Rate_K3_excited*N[1] + self.Rate_kCID[0]*N_He[0]*(1-self.p)
        dR_dt[0] += attachmentRate0
        dR_dt[1] += attachmentRate1
        currentRate =  - attachmentRate0 - attachmentRate1

        for i in range(self.totalAttachmentLevels-1):
            nextRate = - self.Rate_K3[i+1]*N_He[i] + self.Rate_kCID[i+1]*N_He[i+1]
            attachmentRate = currentRate + nextRate
            currentRate = -nextRate
            dR_dt.append(attachmentRate)
            
        dR_dt.append(currentRate)
        return dR_dt


    def begin_simulation(self):


        changing_parameters = self.conditions["variable"]
        changing_parameters_range = self.conditions["variableRange"]

        simulation_duration = int(self.simulation_parameters["Simulation time(ms)"])*1e-3 # sec --> ms
        totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulation_duration_data_points = np.linspace(0, simulation_duration, totalSteps)
        
        self.tspan = [0, simulation_duration]
        initial_temperature = 300

        N = boltzman_distribution(self.Energy, initial_temperature)[:self.totallevel]
        N_He = self.totalAttachmentLevels*[0]
        self.boltzman_distribution_source = (N, [*N, *N_He])[self.includeAttachmentRate]
        

        if changing_parameters == "time":

            nHe = float(self.rate_coefficients["He density(cm3)"])
            power = float(self.power_broadening["power(W)"])
            Noff, Non = self.get_simulation_results(nHe, power)
            resOffCounts = Noff.sol(self.simulation_duration_data_points)
            resOnCounts = Non.sol(self.simulation_duration_data_points)
            self.plot_results(changing_parameters, resOnCounts, resOffCounts)

        elif changing_parameters == "He density(cm3)":

            power = float(self.power_broadening["power(W)"])
            resOffCounts_list = []
            resOnCounts_list = []

            start, end, steps = changing_parameters_range.split(",")
            start = float(start)
            
            end = float(end)
            steps = int(steps)
            variable_range = np.linspace(start, end, steps)

            for index, nHe in enumerate(variable_range):
                
                print(f"Running: {index}\n", flush=True)
                Noff, Non = self.get_simulation_results(nHe, power)
            
                resOffCounts = Noff.sol(self.simulation_duration_data_points)
                resOnCounts = Non.sol(self.simulation_duration_data_points)
                resOffCounts_list.append(resOffCounts)
                resOnCounts_list.append(resOnCounts)

            resOffCounts_list = np.array(resOffCounts_list, dtype=np.float)
            resOnCounts_list = np.array(resOnCounts_list, dtype=np.float)

            off_counts = []
            on_counts = []
            
            for i in range(steps):

                off_counts.append(resOffCounts_list[i, self.totallevel, -1])
                on_counts.append(resOnCounts_list[i, self.totallevel, -1])
            
            off_counts = np.array(off_counts, dtype=np.float)
            on_counts = np.array(on_counts, dtype=np.float)
            signal = (1 - (on_counts / off_counts))*100

            self.plot_results(changing_parameters, x=variable_range, y=signal)
        
        elif changing_parameters == "Power(W)":

            nHe = float(self.rate_coefficients["He density(cm3)"])
            resOffCounts_list = []
            resOnCounts_list = []

            start, end, steps = changing_parameters_range
            start = float(start)
            end = float(end)
            steps = int(steps)
            variable_range = np.linspace(start, end, steps)

            for index, power in enumerate(variable_range):
                
                print(f"Running: {index}\n", flush=True)
                Noff, Non = self.get_simulation_results(nHe, power)
                resOffCounts = Noff.sol(self.simulation_duration_data_points)
                resOnCounts = Non.sol(self.simulation_duration_data_points)
                resOffCounts_list.append(resOffCounts)
                resOnCounts_list.append(resOnCounts)
            


            resOffCounts_list = np.array(resOffCounts_list, dtype=np.float)
            resOnCounts_list = np.array(resOnCounts_list, dtype=np.float)
            off_counts = []
            on_counts = []
            

            for i in range(steps):
                off_counts.append(resOffCounts_list[i, self.totallevel, -1])

                on_counts.append(resOnCounts_list[i, self.totallevel, -1])
            
            off_counts = np.array(off_counts, dtype=np.float)
            on_counts = np.array(on_counts, dtype=np.float)
            signal = (1 - (on_counts / off_counts))*100

            self.plot_results(changing_parameters, x=variable_range, y=signal)


    def get_attachment_rates(self):
        self.Rate_K3 = [float(i.strip())*self.nHe**2 for i in self.rate_coefficients["k3"].split(",")]

        a = float(self.rate_coefficients["a"])
        self.Rate_K3_excited = a*self.Rate_K3[0]
        self.Rate_kCID = [float(i.strip())*self.nHe for i in self.rate_coefficients["kCID"].split(",")]

    def get_simulation_results(self, nHe, power):
        
        self.nHe = nHe
        
        norm = self.lineshape_normalise(power)
        self.A_10 = float(self.einstein_coefficient["A_10"])

        self.B_10 = stimulated_emission(self.A_10, self.freq)*norm
        self.B_01 = stimulated_absorption(self.excitedFrom, self.excitedTo, self.B_10)

        self.get_attachment_rates()
        self.p = float(self.rate_coefficients["branching-ratio"])

        self.lightON=False
        Noff = solve_ivp(self.computeRateDistributionEquations, self.tspan, self.boltzman_distribution_source, dense_output=True)
        resOffCounts = Noff.sol(self.simulation_duration_data_points)

        self.lightON=True
        Non = solve_ivp(self.computeRateDistributionEquations, self.tspan, self.boltzman_distribution_source, dense_output=True)
        resOnCounts = Non.sol(self.simulation_duration_data_points)

        return Noff, Non

    def computeRateDistributionEquations(self, t, counts):

        if self.includeAttachmentRate:
            N =  counts[:-self.totalAttachmentLevels]
            N_He = counts[-self.totalAttachmentLevels:]
        else: N = counts
        
        rateCollection = []
        for i in range(self.totallevel):
            collisional_collection = self.compute_collision_process(i, N)
            einstein_collection = self.compute_einstein_process(i, N)
            collections = collisional_collection + einstein_collection
            rateCollection.append(collections)

        dR_dt = []
        for _ in rateCollection:
            _temp = reduce(lambda a, b: a+b, _)
            dR_dt.append(_temp)
        
        if self.includeAttachmentRate:
            dR_dt = self.compute_attachment_process(N, N_He, dR_dt)
        return dR_dt


    def lineshape_normalise(self, power):

        # doppler line width
        massIon = float(self.lineshape_conditions["IonMass(amu)"])
        tempIon = float(self.lineshape_conditions["IonTemperature(K)"])
        sigma = gauss_fwhm(self.freq, massIon, tempIon)

        # power broadening
        dipoleMoment = float(self.power_broadening["dipoleMoment(D)"])
        

        cp = float(self.power_broadening["cp"])
        gamma = lorrentz_fwhm(dipoleMoment, power, cp)

        # normalised line shape factor
        LineShape = voigt(gamma, sigma)
        
        # transition rate due to influence of mm-wave 
        # normalisation factor

        trap_area = float(self.main_parameters["trap_area"])
        norm = (power/(trap_area*speed_of_light))*LineShape
        print(f"{massIon=}\n{tempIon=}\n{sigma=:.2e}\n{gamma=:.2e}\n{LineShape=:.2e}\n{norm=:.2e}\n", flush=True)

        return norm

    def plot_results(self, changing_parameters, resOnCounts=None, resOffCounts=None, x=None, y=None):

        if changing_parameters == "time":
            fig, (ax, ax1) = plt.subplots(ncols=2, figsize=(12, 4), dpi=100)
            
            legends = [f"{self.molecule}{i}" for i in range(self.totallevel)]
            if self.includeAttachmentRate:
                legends += [f"{self.molecule}He"]
                legends += [f"{self.molecule}{self.taggingPartner}{i+1}" for i in range(1, self.totalAttachmentLevels)]

            simulateTime_ms = self.simulation_duration_data_points*1e3
            counter = 0

            for on, off in zip(resOnCounts, resOffCounts):
                ax.plot(simulateTime_ms, on, f"-C{counter}", label=legends[counter])
                ax.plot(simulateTime_ms, off, f"--C{counter}")
                counter += 1
                
            ax.plot(simulateTime_ms, resOnCounts.sum(axis=0), "k")

            ax.legend(title=f"-ON, --OFF")
            ax.set(yscale="log", ylabel="Counts", xlabel="Time(ms)")
            ax.minorticks_on()

            
            signal_index = self.totallevel+1

            signal = (1 - (resOnCounts[signal_index][1:] / resOffCounts[signal_index][1:]))*100
            ax1.plot(simulateTime_ms[1:], signal)
            ax1.legend([f"Max. Signal = {signal.max():.2f} at {(simulateTime_ms[1:][signal.argmax()]):.2f}ms"])
            ax1.minorticks_on()
            ax1.set(title="Signal as a function of trap time", xlabel="Time (ms)", ylabel="Signal (%)")
            plt.tight_layout()
            plt.show()

        else:

            fig, ax = plt.subplots(figsize=(7, 5), dpi=100)

            legends = [f"{self.molecule}{i}" for i in range(self.totallevel)]

            print(x, y)
            ax.plot(x, y, ".-")

            ax.legend(legends)
            ax.set(ylabel="Signal(%)", xlabel="Time(ms)")
            
            ax.minorticks_on()
            plt.tight_layout()
            plt.show()

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    conditions = json.loads(", ".join(args))

    ROSAA(conditions)