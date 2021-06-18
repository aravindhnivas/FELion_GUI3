
import sys, json
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import speed_of_light
from functools import reduce
from scipy.integrate import solve_ivp

from pathlib import Path as pt
from ROSAA_func import distribution, boltzman_distribution, \
    stimulated_absorption, stimulated_emission,\
    voigt, lorrentz_fwhm, gauss_fwhm

from time import perf_counter
from FELion_constants import colors
class ROSAA():

    def __init__(self, conditions):


        self.conditions = conditions
        self.currentLocation = conditions["currentLocation"]
        self.filename = conditions["filename"]
        self.writefile = conditions["writefile"]
        if self.writefile: 
            self.save_parameters_to_file()

        self.deconstruct_parameters()
        if self.includeCollision: 
            self.get_collisional_rates()

        self.time_start = perf_counter()
        self.begin_simulation()


    def save_parameters_to_file(self):

        with open(pt(self.currentLocation) / f"{self.filename}.json", 'w+') as f:
        
            data = json.dumps(self.conditions, sort_keys=True, indent=4, separators=(',', ': '))
            f.write(data)

        
            
    def deconstruct_parameters(self):

        self.main_parameters = self.conditions["main_parameters"]
        self.simulation_parameters = self.conditions["simulation_parameters"]

        self.einstein_coefficient = {q:float(value) for q, value in self.conditions["einstein_coefficient"].items()}
        print(f"{self.einstein_coefficient=}", flush=True)
        self.lineshape_conditions = self.conditions["lineshape_conditions"]
        self.rate_coefficients = self.conditions["rate_coefficients"]

        self.power_broadening = self.conditions["power_broadening"]

        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]
        self.includeCollision = conditions["includeCollision"]

        self.includeAttachmentRate = conditions["includeAttachmentRate"]
        self.totallevel = int(conditions["numberOfLevels"])
        self.totalAttachmentLevels = int(self.rate_coefficients["totalAttachmentLevels"])
        self.trapTemp = float(self.conditions["trapTemp"])

        self.energyUnit = self.conditions["energyUnit"]
        speed_of_light_in_cm = speed_of_light*100

        self.energy_levels = {} # in cm-1
        print(f"{list(self.conditions['energy_levels'].keys())=}")
        for label, value in self.conditions["energy_levels"].items():
            value = float(value)
            if self.energyUnit == "MHz":
                value = (value*1e6)/speed_of_light_in_cm
            self.energy_levels[label.rstrip()] = value
        print(f"{self.energy_levels=}", flush=True)

        self.total_energy_levels = len(self.energy_levels)
        self.excitedTo = str(self.simulation_parameters["excitedTo"])
        self.excitedFrom = str(self.simulation_parameters["excitedFrom"])

        

        # self.freq = float(self.main_parameters["freq"])
        
        self.freq = abs(self.energy_levels[self.excitedTo] - self.energy_levels[self.excitedFrom]) # in cm-1
        self.freq = self.freq*speed_of_light_in_cm # in cm-1*cm/s --> Hz

        print(f"{self.freq=}")

        self.molecule = self.main_parameters["molecule"]

        self.taggingPartner = self.main_parameters["tagging partner"]
        self.electronSpin = self.conditions["electronSpin"]

        self.zeemanSplit = self.conditions["zeemanSplit"]

    def get_collisional_rates(self):

        collisional_rates = {q:float(value) for q, value in self.conditions["collisional_rates"].items()}
        
        q_deexcitation_mode = self.conditions["deexcitation"]
        rates = {}

        for key in collisional_rates.keys():
            if q_deexcitation_mode:
                excited, ground = key.split(" --> ")
            else:
                ground, excited = key.split(" --> ")

            deexciteRateConstantKey = f"{excited} --> {ground}"
            exciteRateConstantKey = f"{ground} --> {excited}"

            if q_deexcitation_mode:
                _temp = collisional_rates[deexciteRateConstantKey]
                rates[deexciteRateConstantKey] = _temp

                rates[exciteRateConstantKey] = _temp*distribution(ground, excited, self.energy_levels, self.trapTemp, self.electronSpin, self.zeemanSplit )
            else:
                _temp = collisional_rates[exciteRateConstantKey]
                rates[exciteRateConstantKey] = _temp
                
                rates[deexciteRateConstantKey] = _temp * distribution(excited, ground, self.energy_levels, self.trapTemp, self.electronSpin, self.zeemanSplit )
        self.collisional_rates = rates

        print(f"{self.collisional_rates=}", flush=True)

    def compute_collision_process(self, i, N):
    
        collections = []

        for j in range(self.totallevel):
            if i!= j: 
                
                key = f"{j} --> {i}"
                keyInverse = f"{i} --> {j}"
                k = self.collisional_rates[key]*self.nHe*N[j] - self.collisional_rates[keyInverse]*self.nHe*N[i]
                collections.append(k)
        return collections


    
    
    
    def compute_einstein_process(self, i, N):

        collections = []
        if self.includeSpontaneousEmission:

            # Einstein Coefficient A
            
            if i == 0:
                temp_from = self.einstein_coefficient[f"{i+1} --> {i}"]*N[i+1]
                collections.append(temp_from)

            elif i<self.totallevel-1:

                temp_from = self.einstein_coefficient[f"{i+1} --> {i}"]*N[i+1]
                temp_to = -self.einstein_coefficient[f"{i} --> {i-1}"]*N[i]

                collections.append(temp_from)
                collections.append(temp_to)
            elif i == self.totallevel-1:

                temp_to = -self.einstein_coefficient[f"{i} --> {i-1}"]*N[i]

                collections.append(temp_to)


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

    def compute_attachment_process(self, N_He, ion_counts):
    
        # energy_keys = self.energy_levels.keys()
        # ion_counts = {key: value for key, value in zip(energy_keys, dR_dt)}
        if self.includeCollision:
            attachmentRate0 = - self.Rate_K3[0]*ion_counts[self.excitedFrom] + self.Rate_kCID[0]*N_He[0]*self.p
            attachmentRate1 = - self.Rate_K3_excited*ion_counts[self.excitedTo] + self.Rate_kCID[0]*N_He[0]*(1-self.p)
            
            ion_counts[self.excitedFrom] += attachmentRate0
            ion_counts[self.excitedTo] += attachmentRate1

        else:
            
            forward_reaction_0 = - self.Rate_K3[0]*ion_counts[self.excitedFrom]
            ion_counts[self.excitedFrom] += forward_reaction_0

            forward_reaction_1 = - self.Rate_K3_excited*ion_counts[self.excitedTo]
            ion_counts[self.excitedTo] += forward_reaction_1

            # for the first complex formed (sign not corrected)
            attachmentRate0 =  forward_reaction_0 + self.Rate_kCID[0]*N_He[0]*self.p
            attachmentRate1 = forward_reaction_1 + self.Rate_kCID[0]*N_He[0]*(1-self.p)

        dR_dt = list(ion_counts.values())

        # for the first complex formed (sign corrected)
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

        self.total_trap_time = int(self.simulation_parameters["Simulation time(ms)"])
        self.simulation_duration = self.total_trap_time*1e-3 # ms --> sec

        self.totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulation_duration_data_points = np.linspace(0, self.simulation_duration, self.totalSteps)
        self.tspan = [0, self.simulation_duration]
        self.initial_temperature = 300
        if self.includeCollision:
            N = boltzman_distribution(self.energy_levels, self.initial_temperature, self.electronSpin, self.zeemanSplit)
        else:
            self.boltzman_ratio = boltzman_distribution(self.energy_levels, self.trapTemp, self.electronSpin, self.zeemanSplit)

            print(f"{self.boltzman_ratio.sum()=}", flush=True)
            print(f"{self.boltzman_ratio=}\n{self.boltzman_ratio.sum()=}", flush=True)

        if self.includeAttachmentRate:
            
            
            self.boltzman_distribution_source = np.append(self.boltzman_ratio, np.zeros(self.totalAttachmentLevels))
        else:

            self.boltzman_distribution_source = self.boltzman_ratio

        def run_for_each(const, run_type="nHe"):

            start, end, steps = changing_parameters_range.split(",")

            start = float(start)
            end = float(end)
            steps = int(steps)
            variable_range = np.linspace(start, end, steps)

            print(f"{start=:.2e}==>{end=:.2e} in {steps=}\n", flush=True)

            resOffCounts_list = []
            resOnCounts_list = []

            for index, var in enumerate(variable_range):
                print(f"Running ({run_type}): {index}: {var=:.2e}\n", flush=True)
                time_start = perf_counter()
                if run_type=="nHe":
                    Noff, Non = self.get_simulation_results(var, const)

                else:
                    Noff, Non = self.get_simulation_results(const, var)

                resOffCounts = Noff.sol(self.simulation_duration_data_points)
                resOnCounts = Non.sol(self.simulation_duration_data_points)
                resOffCounts_list.append(resOffCounts)
                resOnCounts_list.append(resOnCounts)
                print(f"Time taken for run-{index} ({var=:.2e}): {round(perf_counter()-time_start, 2)} s", flush=True)
                print(f"Total time taken: {round(perf_counter()-self.time_start, 2)} s", flush=True)
            resOffCounts_list = np.array(resOffCounts_list, dtype=np.float)
            resOnCounts_list = np.array(resOnCounts_list, dtype=np.float)

            off_counts = []
            on_counts = []
            for i in range(steps):
                off_counts.append(resOffCounts_list[i, self.total_energy_levels, -1])
                on_counts.append(resOnCounts_list[i, self.total_energy_levels, -1])
            
            off_counts = np.array(off_counts, dtype=np.float)
            on_counts = np.array(on_counts, dtype=np.float)
            signal = (1 - (on_counts / off_counts))*100
            print(f"Total time taken for simulation: {round(perf_counter()-self.time_start, 2)} s", flush=True)
            
            if self.writefile:
                self.write_data_to_file(changing_parameters, changing_parameters_range, resOnCounts_list, resOffCounts_list, signal)
            self.plot_results(changing_parameters, x=variable_range, y=signal)


        if changing_parameters == "time":

            nHe = float(self.rate_coefficients["He density(cm3)"])
            power = float(self.power_broadening["power(W)"])
            Noff, Non = self.get_simulation_results(nHe, power)
            resOffCounts = Noff.sol(self.simulation_duration_data_points)
            resOnCounts = Non.sol(self.simulation_duration_data_points)

            print(f"Time taken to simulation: {round(perf_counter()-self.time_start, 2)} s", flush=True)

            savefile = pt(self.currentLocation)/self.filename
            if self.writefile:
                f = open(f"{savefile}_{self.excitedFrom}--{self.excitedTo}_raw_data.dat", "w+")
                f.write(f"############################## Begin: Run ##############################\n")
                self.write_signal_file(f, resOnCounts.T, resOffCounts.T)
                f.write(f"############################## END: Run ##############################\n\n")
                f.close()

            if self.includeAttachmentRate and self.writefile:

                with open(f"{savefile}_{self.excitedFrom}--{self.excitedTo}_signal.dat", "w+") as f:
                    f.write(f"# Time(ms) \tSignal (%)\n")
                    f.write(f"# Time evolution (s): 0, {self.simulation_duration}, {self.totalSteps}\n")
                    simulateTime_ms = self.simulation_duration_data_points*1e3
                    signal_index = self.total_energy_levels+1
                    signal = (1 - (resOnCounts[signal_index][1:] / resOffCounts[signal_index][1:]))*100
                    for var, sig in zip(simulateTime_ms[1:], signal):
                        f.write(f"{var:.2f}\t{sig:.2f}\n")
            
            if self.includeAttachmentRate:
                signal_index = self.total_energy_levels+1

                signal = (1 - (resOnCounts[signal_index][1:] / resOffCounts[signal_index][1:]))*100
                print(f"{signal[-1]=}")
            self.plot_results(changing_parameters, resOnCounts, resOffCounts)

        elif changing_parameters == "He density(cm3)":
            power = float(self.power_broadening["power(W)"])
            run_for_each(power, run_type="nHe")
            
        elif changing_parameters == "Power(W)":
            nHe = float(self.rate_coefficients["He density(cm3)"])
            run_for_each(nHe, run_type="power")

    def get_attachment_rates(self):

        self.Rate_K3 = [float(i.strip())*self.nHe**2 for i in self.rate_coefficients["k3"].split(",")]
        a = float(self.rate_coefficients["a(k31)"])
        self.Rate_K3_excited = a*self.Rate_K3[0]
        print(f"{self.Rate_K3=}", flush=True)

        self.Rate_kCID = [float(i.strip())*self.nHe for i in self.rate_coefficients["kCID"].split(",")]
        print(f"{self.Rate_kCID=}", flush=True)

    def get_simulation_results(self, nHe, power):
        self.nHe = nHe
        print(f"{nHe=:.2e}\n{power=:.2e}", flush=True)
        norm = self.lineshape_normalise(power)
        self.A_10 = float(self.einstein_coefficient[f"{self.excitedTo} --> {self.excitedFrom}"])
        self.B_10 = stimulated_emission(self.A_10, self.freq)*norm
        self.B_01 = stimulated_absorption(self.excitedFrom, self.excitedTo, self.B_10, self.electronSpin, self.zeemanSplit)

        print(f"{self.B_01=}\n{self.B_10=}", flush=True)
        # self.B_rate = self.B_01*ion_counts[f"{self.excitedFrom}"] - self.B_10*ion_counts[f"{self.excitedTo}"]

        self.get_attachment_rates()
        self.p = float(self.rate_coefficients["branching-ratio(kCID)"])
        self.lightON=False
        Noff = solve_ivp(self.computeRateDistributionEquations, self.tspan, self.boltzman_distribution_source, dense_output=True)


        resOffCounts = Noff.sol(self.simulation_duration_data_points)
        print(f"{resOffCounts.shape=}")

        self.lightON=True

        Non = solve_ivp(self.computeRateDistributionEquations, self.tspan, self.boltzman_distribution_source, dense_output=True)
        resOnCounts = Non.sol(self.simulation_duration_data_points)
        
        print(f"{resOnCounts.shape=}")
        return Noff, Non


    def computeRateDistributionEquations(self, t, counts):

        if self.includeAttachmentRate:
            N = counts[:-self.totalAttachmentLevels]
            N_He = counts[-self.totalAttachmentLevels:]
        else: N = counts

        if not self.includeCollision:
            N = N.sum()*self.boltzman_ratio/self.boltzman_ratio.sum()
            print(f"{t}\n{N.sum()=}\t{self.boltzman_ratio.sum()=}")

            ion_counts = {key: value for key, value in zip(self.energy_levels.keys(), N)}
            if self.lightON:
                sum_of_two_level = np.sum([ion_counts[self.excitedFrom], ion_counts[self.excitedTo]])
                ratio = 0.5
                ion_counts[self.excitedTo] = ratio*sum_of_two_level
                ion_counts[self.excitedFrom] = (1-ratio)*sum_of_two_level
        if self.includeAttachmentRate:
            dR_dt = self.compute_attachment_process(N_He, ion_counts)
        else:
            dR_dt = list(ion_counts.values())
        dR_dt = np.array(dR_dt, dtype=np.float)
        return dR_dt

    def lineshape_normalise(self, power):

        # doppler line width
        massIon = float(self.lineshape_conditions["IonMass(amu)"])
        tempIon = float(self.lineshape_conditions["IonTemperature(K)"])
        sigma = gauss_fwhm(self.freq, massIon, tempIon)

        # power broadening
        dipoleMoment = float(self.power_broadening["dipoleMoment(D)"])
        
        trap_area = float(self.main_parameters["trap_area"])
        cp = float(self.power_broadening["cp"])
        gamma = lorrentz_fwhm(dipoleMoment, power, cp, trap_area)

        # normalised line shape factor
        LineShape = voigt(gamma, sigma)
        # normalisation factor
        norm = (power/(trap_area*speed_of_light))*LineShape
        
        print(f"{massIon=}\n{tempIon=}\n{sigma=:.2e}\n{gamma=:.2e}\n{LineShape=:.2e}\n{norm=:.2e}\n", flush=True)
        return norm


    def plot_results(self, changing_parameters, resOnCounts=None, resOffCounts=None, x=None, y=None):

        if changing_parameters == "time":
            fig, (ax, ax1) = plt.subplots(ncols=2, figsize=(12, 7), dpi=100)

            legends = [f"{self.molecule} ({key.strip()})" for key in self.energy_levels.keys()]
            print(legends)
            if self.includeAttachmentRate:
                legends += [f"{self.molecule}{self.taggingPartner}"]
                legends += [f"{self.molecule}{self.taggingPartner}$_{i+1}$" for i in range(1, self.totalAttachmentLevels)]
            simulateTime_ms = self.simulation_duration_data_points*1e3
            # print(f"{simulateTime_ms=}")
            
            colorSchemes = []
            for color in colors[::2]:
                scale = 1/255
                temp = [_*scale for _ in color]
                colorSchemes.append(temp)
            counter = 0
            for on, off in zip(resOnCounts, resOffCounts):
                ax.plot(simulateTime_ms, on, ls="-", c=colorSchemes[counter], label=f"{legends[counter]}")
                ax.plot(simulateTime_ms, off, ls="--", c=colorSchemes[counter])
                counter += 1

            # ax.plot(simulateTime_ms, resOnCounts.sum(axis=0), "-k", label="Total SUM (ON)")
            # ax.plot(simulateTime_ms, resOffCounts.sum(axis=0), "--k", label="Total SUM (OFF)")
            
            ax.axhline(1, xmin=0, xmax=self.total_trap_time, c="k", ls="-.")
            legend_axis = ax.legend(title="-ON, --OFF", fontsize=12, title_fontsize=12)
            # legend_axis.set_title("-ON, --OFF", fontsize=12)
            legend_axis.set_draggable(True)

            ax.set(yscale="log")
            ax.set_xlabel("Time(ms)", fontsize=16)
            ax.set_ylabel("Counts", fontsize=16)
            
            if self.includeAttachmentRate:

                signal_index = self.total_energy_levels+1
                
                
                start_index = 1
                
                signal = (1 - (resOnCounts[signal_index][start_index:] / resOffCounts[signal_index][start_index:]))*100
                ax1.plot(simulateTime_ms[1:], signal, ".-")
                ax1.legend([f"Signal = {signal[-1]:.2f} (%) at {simulateTime_ms[-1]:.0f}ms"], fontsize=16)
                ax1.set_title("Signal as a function of trap time", fontsize=18)
                ax1.set_xlabel("Time(ms)", fontsize=16)
                ax1.set_ylabel("Signal (%)", fontsize=16)

            for axes in (ax, ax1):
                axes.minorticks_on()
                axes.tick_params(axis='both', labelsize=16)
                axes.tick_params(which='both', width=2)
                axes.tick_params(which='major', length=7)
                axes.tick_params(which='minor', length=4)

            plt.tight_layout()

            plt.show()

        else:
            fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
            
            legends = [f"{self.molecule}{i}" for i in range(self.total_energy_levels)]
            ax.plot(x, y, ".-", label=f"{self.molecule}-{self.taggingPartner}")
            ax.legend()
            ax.set(ylabel="Signal(%)", xlabel=changing_parameters)
            ax.minorticks_on()
            plt.tight_layout()
            plt.ticklabel_format(axis="x", style="sci", scilimits=(0,0))
            plt.show()

    def write_data_to_file(self, changing_parameters, changing_parameters_range, resOnCounts_list, resOffCounts_list, signal):

        start, end, steps = changing_parameters_range.split(",")
        start = float(start)
        end = float(end)
        steps = int(steps)
        variable_range = np.linspace(start, end, steps)

        savefile_name = f"{self.filename}_{changing_parameters.split('(')[0]}_{start:.1e}-{end:.1e}"
        savefile = pt(self.currentLocation)/savefile_name
        
        f = open(f"{savefile}_{self.excitedFrom}--{self.excitedTo}_raw_data.dat", "w+")

        # with open(f"{savefile}_raw_data.dat", "w+") as f:
        f.write(f"# {changing_parameters}: {changing_parameters_range}\n")
        f.write(f"# Time evolution (s): 0, {self.simulation_duration}, {self.totalSteps}\n")
        for index, var in enumerate(variable_range):
            f.write(f"############################## Begin: Run_{index}: {var} ##############################\n")

            data_on = resOnCounts_list[index].T
            data_off = resOffCounts_list[index].T
            self.write_signal_file(f, data_on, data_off)
            f.write(f"############################## END: Run_{index}: {var} ##############################\n\n")
        f.close()


        if self.includeAttachmentRate:
            with open(f"{savefile}_{self.excitedFrom}--{self.excitedTo}_signal.dat", "w+") as f:
                f.write(f"# {changing_parameters}\tSignal (%)\n")
                for var, sig in zip(variable_range, signal):
                    f.write(f"{var:.2e}\t{sig:.2f}\n")

        print(f"File written: {savefile}")


    def write_signal_file(self, f, data_on, data_off):

        f.write(f"# Time evolution (s): 0, {self.simulation_duration}, {self.totalSteps}\n")
        f.write("# lightOFF\n")

        legends = [f"{self.molecule}({key.strip()})" for key in self.energy_levels.keys()]
        if self.includeAttachmentRate:
            legends += [f"{self.molecule}{self.taggingPartner}"]
            legends += [f"{self.molecule}{self.taggingPartner}{i+1}" for i in range(1, self.totalAttachmentLevels)]

        f.write("#" + "\t".join([f'{i}' for i in legends]) + "\n")
        for off in data_off:
            f.write("\t".join([f'{i}' for i in off])+"\n")
        f.write("# lightON\n")
        for on in data_on: 
            f.write("\t".join([f'{i}' for i in on])+"\n")


if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    conditions = json.loads(", ".join(args))
    print(conditions, flush=True)
    ROSAA(conditions)