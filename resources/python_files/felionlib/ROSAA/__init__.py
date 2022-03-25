
import json
import time
import numpy as np
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from .definitions import boltzman_distribution
from .voigt import main as getLineShape
from felionlib.utils.optimizePlot import optimizePlot
from felionlib.utils.FELion_constants import pltColors
from felionlib.utils.FELion_widgets import FELion_Tk


def log(msg): 
    return print(msg, flush=True)


speedOfLight = 299792458
speedOfLightIn_cm = speedOfLight*100


class ROSAA:

    def __init__(self, nHe=None, power=None, plotGraph=True, writefile=None):

        self.energyUnit = conditions["energyUnit"]
        convertNorm_to_wn = 1e6/speedOfLightIn_cm if self.energyUnit == "MHz" else 1
        self.energyLevels = {key: float(value)*convertNorm_to_wn for key, value in conditions["energy_levels"].items()}
            
        self.energyKeys = list(self.energyLevels.keys())
        self.lineshape_conditions = conditions["lineshape_conditions"]
        self.collisionalTemp = float(conditions["collisionalTemp"])

        self.collisionalRateConstants = {key: float(value) for key, value in conditions["collisional_rates"].items()}
        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]
        self.includeCollision = conditions["includeCollision"]
        
        if self.includeSpontaneousEmission:
            self.einsteinA_Rates = {key: float(value) for key, value in conditions["einstein_coefficient"]["A"].items()}

            self.power = power
            if self.power is None:
                self.power = float(conditions['power_broadening']['power(W)'])

            self.computeEinsteinBRates()

            print(f"{self.power=}", flush=True)

        self.excitedFrom = str(conditions["excitedFrom"])
        self.excitedTo = str(conditions["excitedTo"])
        self.transitionLevels = [self.excitedFrom, self.excitedTo]

        self.start_time = time.perf_counter()
        
        self.writefile = writefile
        if self.writefile is None:
            self.writefile = conditions["writefile"]
        
        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]

        self.simulation_parameters = conditions["simulation_parameters"]
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])

        self.boltzmanDistribution = boltzman_distribution( self.energyLevels, initialTemp, self.electronSpin, self.zeemanSplit )
        self.boltzmanDistributionCold = boltzman_distribution( self.energyLevels, self.collisionalTemp, self.electronSpin, self.zeemanSplit )
        
        
        self.molecule = conditions["main_parameters"]["molecule"]
        self.taggingPartner = conditions["main_parameters"]["tagging partner"]
        self.GetAttachmentRatesParameters()

        self.legends = []
        for key in self.energyKeys:
            key = key.strip()
            if "_" in key:
                key = key.split("_")
                key = key[0] + "_{" + key[1] + "}"
            label = f"{self.molecule}(${key}$)"
            self.legends.append(label)

        if self.includeAttachmentRate:
            self.legends += [f"{self.molecule}{self.taggingPartner}"]
            self.legends += [f"{self.molecule}{self.taggingPartner}$_{i+1}$" for i in range(1, self.totalAttachmentLevels)]

        self.fixedPopulation = conditions["simulationMethod"] == "FixedPopulation"

        self.transitionTitleLabel = f"${self.excitedFrom}-{self.excitedTo}$"
        if "_" in self.excitedFrom:
            lgfrom = self.excitedFrom.split("_")
            lgto = self.excitedTo.split("_")
            self.transitionTitleLabel = f"{self.molecule}: ${lgfrom[0]}_"+ "{"+f"{lgfrom[1]}"+"} - "+f"{lgto[0]}_"+ "{"+f"{lgto[1]}"+"}$"

        if nHe is None:
            nHe = float(conditions["numberDensity"])

        self.withoutCollisionalConstants = conditions["simulationMethod"] == "withoutCollisionalConstants"
        if self.fixedPopulation or self.withoutCollisionalConstants:
            self.simulateFixedPopulation(nHe)
            log(f"{self.boltzmanDistributionCold=}")
        else:
            self.Simulate(nHe)

        if plotGraph: self.Plot()

    def computeEinsteinBRates(self):
        trapArea = float(conditions['main_parameters']['trap_area (sq-meter)'])
        constantTerm = self.power/(float(trapArea)*speedOfLight)

        gaussian = float(conditions["gaussian"])
        lorrentz = float(conditions["lorrentz"])
        lineShape = getLineShape({"gaussian": gaussian, "lorrentz": lorrentz})
        
        norm = constantTerm*lineShape
        einsteinB_RateConstants = conditions["einstein_coefficient"]["B_rateConstant"]
        self.einsteinB_Rates = {key: float(value)*norm for key, value in einsteinB_RateConstants.items()}
        print(f"{self.einsteinB_Rates=}", flush=True)
        
    def simulateFixedPopulation(self, nHe):
        self.includeAttachmentRate = False
        t_limit = 0.001

        if self.withoutCollisionalConstants:
            ratio = self.simulate_without_CollisionConstants()
        else:
            self.Simulate(nHe, duration=t_limit)
            ratio = self.lightON_distribution.T[-1]

        self.includeCollision = False
        self.includeAttachmentRate = True
        self.Simulate(nHe, t0=t_limit, ratio=ratio)
        
        ON_fixedPopulation_arr = np.array([ratio*(1-np.sum(NHE)) for NHE in self.lightON_distribution.T]).T
        self.lightON_distribution = np.array(ON_fixedPopulation_arr.tolist()+self.lightON_distribution.tolist())

        OFF_fixedPopulation_arr = np.array([self.boltzmanDistributionCold*(1-np.sum(NHE)) for NHE in self.lightOFF_distribution.T]).T
        self.lightOFF_distribution = np.array(OFF_fixedPopulation_arr.tolist()+self.lightOFF_distribution.tolist())

    def simulate_without_CollisionConstants(self):

        N = {key: value for key, value in zip(self.energyKeys, self.boltzmanDistributionCold)}
        
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
        norm = G0 + G1
        N[self.excitedFrom] = (G0/norm)*twoLeveltotal
        N[self.excitedTo] = (G1/norm)*twoLeveltotal

        return np.array(list(N.values()), dtype=float)

    def SimulateODE(self, t, counts, nHe, lightON, ratio):
        
        global logCounter
        if self.includeAttachmentRate and self.includeCollision:
            N = counts[:-self.totalAttachmentLevels]
            N_He = counts[-self.totalAttachmentLevels:]
        elif self.includeCollision: N = counts
        else: N_He = counts

        if self.includeCollision:

            dR_dt = []
            
            N = {key: value for key, value in zip(self.energyKeys, N)}
            
            for i in self.energyKeys:
                einstein = []
                collisional = []
                attachment = []

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

                if self.includeAttachmentRate:
                    if i == self.excitedFrom:
                        attachmentRate0 = -(self.k3[0] * nHe**2 * N[i]) + (self.kCID[0] * nHe * N_He[0] * self.kCID_branch)
                        attachment.append(attachmentRate0)
                    
                    elif i == self.excitedTo:
                        attachmentRate1 =  -(self.k31_excited * nHe**2 *  N[i]) + (self.kCID[0] * nHe * N_He[0] * (1-self.kCID_branch))

                        attachment.append(attachmentRate1)

                if self.includeCollision: 
                    collections = np.array(collisional + einstein + attachment).sum()
                    dR_dt.append(collections)

        dRdt_N_He = []

        if self.includeAttachmentRate:
            
            if not self.includeCollision:

                N = (ratio/ratio.sum())*(1-np.sum(N_He))
                _from = self.energyKeys.index(self.excitedFrom)
                _to = self.energyKeys.index(self.excitedTo)

                attachmentRate0 = -(self.k3[0] * nHe**2 * N[_from]) + (self.kCID[0] * nHe * N_He[0] * self.kCID_branch)
                attachmentRate1 =  -(self.k31_excited * nHe**2 *  N[_to]) + (self.kCID[0] * nHe * N_He[0] * (1-self.kCID_branch))

            currentRate = -(attachmentRate0 + attachmentRate1)

            for i in range(len(N_He)-1):

                nextRate = -(self.k3[i+1] * nHe**2 *N_He[i]) + (self.kCID[i+1] * nHe * N_He[i+1])
                attachmentRate = currentRate + nextRate

                dRdt_N_He.append(attachmentRate)
                if self.includeCollision:
                    dR_dt.append(attachmentRate)

                currentRate = -nextRate

            dRdt_N_He.append(currentRate)
            if self.includeCollision:
                dR_dt.append(currentRate)

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
    
    def Simulate(self, nHe, duration=None, t0=0, ratio=[]):

        if not duration:
            duration = self.simulation_parameters["Simulation time(ms)"]
            duration = float(duration)*1e-3 # converting ms ==> s
        
        # t0 = 0.005 if self.fixedPopulation else 0
        if duration <= t0:
            duration = t0*5
        tspan = [t0, duration]

        totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulateTime = np.linspace(t0, duration, totalSteps)

        # Simulation start

        start_time = time.perf_counter()
        N = np.copy(self.boltzmanDistribution) if self.includeCollision else []
        N_He = self.totalAttachmentLevels*[0] if self.includeAttachmentRate else []
        ode_method = "Radau"
        options = {
            "method": ode_method,
            "t_eval": self.simulateTime,
        }

        y_init = [*N, *N_He]
        N_OFF = solve_ivp(self.SimulateODE, tspan, y_init, args=(nHe, False, self.boltzmanDistributionCold), **options )
        log(f'{N_OFF.nfev=} evaluations required.')
        self.lightOFF_distribution = N_OFF.y

        # Boltzmann ratio check when lightOFF
        # ratio = self.lightOFF_distribution.T[-1]
        # differenceWithBoltzman = np.around(self.boltzmanDistributionCold-ratio[:-self.totalAttachmentLevels], 3)
        # log(f"\n{ratio=}\n{self.boltzmanDistributionCold=}\n{differenceWithBoltzman=}\n")

        N_ON = solve_ivp(self.SimulateODE, tspan, y_init, args=(nHe, True, ratio), **options )
        
        self.lightON_distribution = N_ON.y
        log(f'{N_ON.nfev=} evaluations required.')

        # Ratio check after equilibrium
        # OFF_full_ratio = np.array([r/r.sum() for r in self.lightOFF_distribution[:-self.totalAttachmentLevels].T])
        # ON_full_ratio = np.array([r/r.sum() for r in self.lightON_distribution[:-self.totalAttachmentLevels].T])
        # log(f"{np.around(OFF_full_ratio[-1], 2)=}")
        # log(f"{np.around(ON_full_ratio[-1], 4)=}")
        # plt.plot(OFF_full_ratio)
        # plt.plot(ON_full_ratio)


        dataToSend = {
            "misc": {
                "ode": {"method": ode_method},
                "molecule": self.molecule,
                "tag": self.taggingPartner,
                "duration": duration,
                "number-density": f"{nHe:.2e}"
            },
            "legends": self.legends,
            "time (in s)": self.simulateTime.tolist(),
            "lightON_distribution": self.lightON_distribution.tolist(),
            "lightOFF_distribution": self.lightOFF_distribution.tolist()
        
        }

        if self.writefile:
            fmtFloatFn = np.format_float_scientific
            name_append = f"full_output_{fmtFloatFn(nHe, 3)}_{fmtFloatFn(self.power, 3)}"
            WriteData(name_append, dataToSend)
        
        end_time = time.perf_counter()
        
        log(f"Current simulation time {(end_time - start_time):.2f} s")
        log(f"Total simulation time {(end_time - self.start_time):.2f} s")


    def Plot(self):

        self.figs_location = output_dir / "figs"
        if not self.figs_location.exists(): self.figs_location.mkdir()

        widget = FELion_Tk(title=f"Population ratio", location=self.figs_location)
        widget.Figure()
        
        ax = widget.make_figure_layout(
            title=self.transitionTitleLabel, 
            xaxis="Time (ms)", yaxis="Population", savename=savefilename
        )

        plotSimulationTime_milliSecond = self.simulateTime*1e3
        counter = 0
        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):
            
            ax.plot(plotSimulationTime_milliSecond, on, ls="-", c=pltColors[counter], label=f"{self.legends[counter]}")
            ax.plot(plotSimulationTime_milliSecond, off, ls="--", c=pltColors[counter])
            counter += 1

        ax.plot(plotSimulationTime_milliSecond, self.lightON_distribution.sum(axis=0), "-k", alpha=0.5)
        ax.plot(plotSimulationTime_milliSecond, self.lightOFF_distribution.sum(axis=0), "--k")
        
        ax.hlines(1, 0, plotSimulationTime_milliSecond[-1]+plotSimulationTime_milliSecond[-1]*0.2, colors='k', linestyles="dashdot")
        widget.plot_legend = ax.legend(title=f"--OFF, -ON", fontsize=14, title_fontsize=16)
        widget.plot_legend.set_draggable(True)
        ax = optimizePlot(ax, xlabel="Time (ms)", ylabel="Population", title=self.transitionTitleLabel)

        if self.includeAttachmentRate:

            signal_index = len(self.energyKeys)+1
            signal = (1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:]))*100

            signal = np.around(np.nan_to_num(signal).clip(min=0), 1)
            widget1 = FELion_Tk("Toplevel", title=f"Signal", location=self.figs_location)
            widget1.Figure()

            # _, ax1 = plt.subplots(figsize=figure["size"], dpi=int(figure["dpi"]))
            
            ax1 = widget1.make_figure_layout(
                title=self.transitionTitleLabel, 
                xaxis="Time (ms)", yaxis="Signal (%)", savename=savefilename
            )
            ax1.plot(plotSimulationTime_milliSecond[1:], signal, label=f"Signal: {round(signal[-1])} (%)")
            ax1 = optimizePlot(ax1, xlabel="Time (ms)", ylabel="Signal (%)", title=self.transitionTitleLabel)

            widget1.plot_legend = ax1.legend()
            
            log(f"Signal: {round(signal[-1])} (%)")

            # if figure["show"]:
            #     plt.show()

        widget.mainloop()

def WriteData(name, dataToSend):

    datas_location = output_dir / "datas"
    
    if not datas_location.exists():
        datas_location.mkdir()
    
    addText = ""
    if not includeAttachmentRate:
        addText = "_no-attachement"

    with open(datas_location / f"{savefilename}{addText}_{name}.json", 'w+') as f:
        data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(data)
        log(f"{savefilename} file written in {location} folder.")

figure = None
figsize = None
location = None
output_dir = None
conditions = None
savefilename = None

includeAttachmentRate=False

def main(arguments):

    global conditions, figure, savefilename, location, output_dir, includeAttachmentRate

    conditions = arguments
    savefilename = conditions["savefilename"]

    location = pt(conditions["currentLocation"])
    output_dir = location / "../output"
    if not output_dir.exists():
         output_dir.mkdir()
    
    figure = conditions["figure"]
    figure["size"] = [int(i) for i in figure["size"].split(",")]
    figure["dpi"] = int(figure["dpi"])

    includeAttachmentRate = conditions["includeAttachmentRate"]

    nHe = float(conditions["numberDensity"])
    variable = conditions["variable"]

    if variable == "time":

        ROSAA(nHe, plotGraph=figure["show"])

    elif variable == "He density(cm3)":
        functionOfVariable("numberDensity")

    elif variable == "Power(W)":
        functionOfVariable("power")


def functionOfVariable(changeVariable="numberDensity"):
    # functionVariables = ("numberDensity", "power")
    constantFactorLabel = "power" if changeVariable=="numberDensity" else "numberDensity" 
    currentnHe = np.format_float_scientific(float(conditions["numberDensity"]), 3)
    currentnPower = np.format_float_scientific(float(conditions['power_broadening']['power(W)']), 3)
    currentConstant = (currentnHe, currentnPower)[changeVariable=='numberDensity']
    currentConstantUnit = ("cm$^3$", "(W)")[changeVariable=='numberDensity']
    variableRange = conditions["variableRange"]

    _start, _end, _steps = variableRange.split(",")
    _start = int(_start.split("e")[-1])
    _end = int(_end.split("e")[-1])

    electronSpin = conditions["electronSpin"]

    counter = _start
    dataList = []

    while counter<_end:
    
        appendDataList = np.linspace(float(f"1e{counter}"), float(f"1e{counter+1}"), int(_steps))
        dataList = np.append(dataList, appendDataList)
        counter += 1
    
    molecule = conditions["main_parameters"]["molecule"]
    taggingPartner = conditions["main_parameters"]["tagging partner"]

    excitedFrom = str(conditions["excitedFrom"])
    excitedTo = str(conditions["excitedTo"])
    
    energyKeys = list(conditions["energy_levels"].keys())

    excitedToIndex = energyKeys.index(excitedTo)
    excitedFromIndex = energyKeys.index(excitedFrom)
    
    populationChange = []
    signalChange = []

    for variable in dataList:

        if changeVariable=="numberDensity":
            currentData = ROSAA(nHe=variable, plotGraph=False, writefile=conditions["writeall"])
        elif changeVariable=="power":
            currentData = ROSAA(power=variable, plotGraph=False, writefile=conditions["writeall"])

        on = currentData.lightON_distribution
        
        changeInPopulationRatioOn =  on[excitedToIndex][-1] / on[excitedFromIndex][-1]
        populationChange.append(changeInPopulationRatioOn)

        if includeAttachmentRate:
            off = currentData.lightOFF_distribution
            signal_index = len(energyKeys)+1
            chnageInSignal = (1 - (on[signal_index][-1] / off[signal_index][-1]))*100
            chnageInSignal = np.around(np.nan_to_num(chnageInSignal).clip(min=0), 1)
            signalChange.append(chnageInSignal)


    widget = FELion_Tk(title=f"Population ratio", location=output_dir/"figs")
    widget.Figure()
    
    if changeVariable=="numberDensity":
        xlabel=f"{currentData.taggingPartner} number density (cm$^{-3})$"
    else:
        xlabel="Power (W)"

    outputFileName = f"{molecule}-{taggingPartner}__{excitedFrom}-{excitedTo}__"
    outputFileName += f"{changeVariable}.{dataList[0]:.0e}-{dataList[-1]:.0e}.{constantFactorLabel}.{currentConstant}"
    outputFileName = outputFileName.replace("$", "")


    title=currentData.transitionTitleLabel
    ylabel = title.split(":")[-1].replace("$", "")
    # quantumState = f"$N{'_J' if electronSpin else ''}$"
    ylabel = f"${ylabel.split('-')[1]}$ / ${ylabel.split('-')[0]}$"

    ax = widget.make_figure_layout(xaxis=xlabel, yaxis=ylabel, title="", savename=outputFileName)
    ax.plot(dataList, populationChange, "-k", label=f"{currentConstant}{currentConstantUnit}")
    ax = optimizePlot(ax, xlabel=xlabel, ylabel=ylabel, title="")

    ax.set(xscale="log")
    widget.plot_legend = ax.legend()
    widget.fig.tight_layout()

    dataToSend = {
        f"variable ({changeVariable})": list(map(lambda num: np.format_float_scientific(num, 3), dataList)),
        "populationChange": np.around(populationChange, 3).tolist(),
        f"constant ({('power', 'numberDensity')[changeVariable=='numberDensity']})": currentConstant
    }

    if includeAttachmentRate:

        widget1 = FELion_Tk("Toplevel", title=f"Signal", location=output_dir/"figs")
        widget1.Figure()
        ax1 = widget1.make_figure_layout(xaxis=xlabel, yaxis="Signal (%)", title="", savename=f"{outputFileName}.signal")
        ax1.plot(dataList, signalChange, "-k")
        ax1 = optimizePlot(ax1, xlabel=xlabel, ylabel="Signal (%)", title="")
        ax1.set(xscale="log")

        dataToSend["signalChange"] = np.around(signalChange, 3).tolist()

    if conditions["writefile"]:

        datas_location = output_dir / "datas"
        if not datas_location.exists():
            datas_location.mkdir()

        with open(datas_location / f"{outputFileName}.txt", 'w+') as f:
            f.write(f"# constant ({('numberDensity', 'power')[changeVariable=='numberDensity']}): ")
            f.write(f"{currentConstant}\n")
            f.write(f"# variable ({changeVariable})\tpopulationChange\n")
        
            counter = 0
            for x, y in zip(dataList, populationChange):
                f.write(f"{x:.3e}\t{y:.3f}")
                f.write(f"\t{signalChange[counter]}\n") if includeAttachmentRate else f.write("\n")
                counter += 1
            log(f"{savefilename} file written in {location} folder.")

    widget.mainloop()
    