import json
import time
import numpy as np
from typing import Literal
from pathlib import Path as pt
from scipy.integrate import solve_ivp
from .definitions import boltzman_distribution
from .voigt import main as getLineShape
from felionlib.utils import logger, remove_special_chars_in_string
from felionlib.utils.FELion_constants import pltColors
from felionlib.utils.felionQt import felionQtWindow
from scipy.constants import speed_of_light

from .plot import main as ROSAA3D_plot


speedOfLightIn_cm = speed_of_light * 100
qapp = None


class ROSAA:
    def __init__(
        self,
        nHe: float,
        power: float,
        k3_branch: float,
        plotGraph=False,
        writefile=None,
        verbose=False,
        save_location: pt = None,
    ):

        self.verbose = verbose
        self.save_location = save_location

        self.energyUnit = conditions["energyUnit"]
        self.numberOfLevels = int(conditions["numberOfLevels"])
        convertNorm_to_wn = 1e6 / speedOfLightIn_cm if self.energyUnit == "MHz" else 1
        self.energyLevels = {
            key: float(value) * convertNorm_to_wn for key, value in conditions["energy_levels"].items()
        }

        self.energyKeys: list[str] = list(self.energyLevels.keys())
        self.lineshape_conditions = conditions["lineshape_conditions"]
        self.collisionalTemp = float(conditions["collisionalTemp"])

        self.collisionalRateConstants = {key: float(value) for key, value in conditions["collisional_rates"].items()}
        self.includeSpontaneousEmission = conditions["includeSpontaneousEmission"]
        self.includeCollision = conditions["includeCollision"]

        if self.includeSpontaneousEmission:
            self.einsteinA_Rates = {key: float(value) for key, value in conditions["einstein_coefficient"]["A"].items()}

            self.power = float(power)
            # if self.power is None:
            #     self.power = float(conditions["power_broadening"]["power(W)"])

            self.computeEinsteinBRates()

            if self.verbose:
                logger(f"{self.power=}")

        self.excitedFrom = str(conditions["excitedFrom"])
        self.excitedTo = str(conditions["excitedTo"])
        self.transitionLevels = [self.excitedFrom, self.excitedTo]

        self.start_time = time.perf_counter()

        self.writefile = writefile or conditions["writefile"]
        # if self.writefile is None:
        #     self.writefile = conditions["writefile"]

        self.electronSpin = conditions["electronSpin"]
        self.zeemanSplit = conditions["zeemanSplit"]

        self.simulation_parameters = conditions["simulation_parameters"]
        initialTemp = float(self.simulation_parameters["Initial temperature (K)"])

        self.boltzmanDistribution = boltzman_distribution(
            self.energyLevels, initialTemp, self.electronSpin, self.zeemanSplit
        )
        self.boltzmanDistributionCold = boltzman_distribution(
            self.energyLevels, self.collisionalTemp, self.electronSpin, self.zeemanSplit
        )

        self.molecule = conditions["main_parameters"]["molecule"]
        self.taggingPartner = conditions["main_parameters"]["tagging partner"]

        self.attachment_rate_coefficients = conditions["attachment_rate_coefficients"]
        self.k3_branch = float(k3_branch)

        if not self.k3_branch:
            raise ValueError("k3_branch is not defined")

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
            self.legends += [
                f"{self.molecule}{self.taggingPartner}$_{i+1}$" for i in range(1, self.totalAttachmentLevels)
            ]

        self.fixedPopulation = conditions["simulationMethod"] == "FixedPopulation"

        self.transitionTitleLabel = f"${self.excitedFrom}-{self.excitedTo}$"
        if "_" in self.excitedFrom:
            lgfrom = self.excitedFrom.split("_")
            lgto = self.excitedTo.split("_")
            self.transitionTitleLabel = (
                f"{self.molecule}: ${lgfrom[0]}_"
                + "{"
                + f"{lgfrom[1]}"
                + "} - "
                + f"{lgto[0]}_"
                + "{"
                + f"{lgto[1]}"
                + "}$"
            )

        # nHe = float(nHe) or float(conditions["nHe"])
        # if nHe is None:
        #     nHe = float(conditions["numberDensity"])

        self.withoutCollisionalConstants = conditions["simulationMethod"] == "withoutCollisionalConstants"
        if self.fixedPopulation or self.withoutCollisionalConstants:
            self.simulateFixedPopulation(nHe)
            if self.verbose:
                logger(f"{self.boltzmanDistributionCold=}")
        else:
            self.Simulate(nHe)

        if plotGraph:
            self.Plot()

    def computeEinsteinBRates(self):
        trapArea = float(conditions["main_parameters"]["trap_area (sq-meter)"])
        constantTerm = self.power / (float(trapArea) * speed_of_light)

        gaussian = float(conditions["gaussian"])
        lorrentz = float(conditions["lorrentz"])
        lineShape = getLineShape({"gaussian": gaussian, "lorrentz": lorrentz}, saveData=False)

        norm = constantTerm * lineShape
        einsteinB_RateConstants = conditions["einstein_coefficient"]["B_rateConstant"]
        self.einsteinB_Rates = {key: float(value) * norm for key, value in einsteinB_RateConstants.items()}
        if self.verbose:
            logger(f"{self.einsteinB_Rates=}")

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

        ON_fixedPopulation_arr = np.array([ratio * (1 - np.sum(NHE)) for NHE in self.lightON_distribution.T]).T
        self.lightON_distribution = np.array(ON_fixedPopulation_arr.tolist() + self.lightON_distribution.tolist())

        OFF_fixedPopulation_arr = np.array(
            [self.boltzmanDistributionCold * (1 - np.sum(NHE)) for NHE in self.lightOFF_distribution.T]
        ).T
        self.lightOFF_distribution = np.array(OFF_fixedPopulation_arr.tolist() + self.lightOFF_distribution.tolist())

    def simulate_without_CollisionConstants(self):

        N = {key: value for key, value in zip(self.energyKeys, self.boltzmanDistributionCold)}

        if not self.zeemanSplit:
            if self.electronSpin:
                j0 = float(self.excitedFrom.split("_")[1])
                j1 = float(self.excitedTo.split("_")[1])
            else:
                j0 = int(self.excitedFrom)
                j1 = int(self.excitedTo)

            G0 = int(2 * j0 + 1)
            G1 = int(2 * j1 + 1)
        else:
            G0 = G1 = 1

        twoLeveltotal = N[self.excitedFrom] + N[self.excitedTo]
        norm = G0 + G1
        N[self.excitedFrom] = (G0 / norm) * twoLeveltotal
        N[self.excitedTo] = (G1 / norm) * twoLeveltotal

        return np.array(list(N.values()), dtype=float)

    def SimulateODE(self, t, counts, nHe, lightON, ratio):

        # global logCounter
        if self.includeAttachmentRate and self.includeCollision:
            N = counts[: -self.totalAttachmentLevels]
            N_He = counts[-self.totalAttachmentLevels :]
        elif self.includeCollision:
            N = counts
        else:
            N_He = counts

        if self.includeCollision:

            dR_dt = []

            N = {key: value for key, value in zip(self.energyKeys, N)}

            for i in self.energyKeys:
                einstein = []
                collisional = []
                attachment = []

                for j in self.energyKeys:
                    if i != j:

                        key = f"{j} --> {i}"
                        keyInverse = f"{i} --> {j}"

                        if self.includeCollision:
                            if key in self.collisionalRateConstants and keyInverse in self.collisionalRateConstants:
                                R_coll = (
                                    self.collisionalRateConstants[key] * N[j]
                                    - self.collisionalRateConstants[keyInverse] * N[i]
                                ) * nHe
                                collisional.append(R_coll)

                            if self.includeSpontaneousEmission:
                                if key in self.einsteinA_Rates:
                                    R_einsteinA = self.einsteinA_Rates[key] * N[j]
                                    einstein.append(R_einsteinA)

                                if keyInverse in self.einsteinA_Rates:
                                    R_einsteinA = -self.einsteinA_Rates[keyInverse] * N[i]
                                    einstein.append(R_einsteinA)

                            if lightON:
                                if i in self.transitionLevels and j in self.transitionLevels:
                                    R_einsteinB = (
                                        self.einsteinB_Rates[key] * N[j] - self.einsteinB_Rates[keyInverse] * N[i]
                                    )
                                    einstein.append(R_einsteinB)

                if self.includeAttachmentRate:
                    if i == self.excitedFrom:
                        attachmentRate0 = -(self.k3[0] * nHe**2 * N[i]) + (
                            self.kCID[0] * nHe * N_He[0] * self.kCID_branch
                        )
                        attachment.append(attachmentRate0)

                    elif i == self.excitedTo:
                        attachmentRate1 = -(self.k31_excited * nHe**2 * N[i]) + (
                            self.kCID[0] * nHe * N_He[0] * (1 - self.kCID_branch)
                        )

                        attachment.append(attachmentRate1)

                if self.includeCollision:
                    collections = np.array(collisional + einstein + attachment).sum()
                    dR_dt.append(collections)

        dRdt_N_He = []

        if self.includeAttachmentRate:

            if not self.includeCollision:

                N = (ratio / ratio.sum()) * (1 - np.sum(N_He))
                _from = self.energyKeys.index(self.excitedFrom)
                _to = self.energyKeys.index(self.excitedTo)

                attachmentRate0 = -(self.k3[0] * nHe**2 * N[_from]) + (
                    self.kCID[0] * nHe * N_He[0] * self.kCID_branch
                )
                attachmentRate1 = -(self.k31_excited * nHe**2 * N[_to]) + (
                    self.kCID[0] * nHe * N_He[0] * (1 - self.kCID_branch)
                )

            currentRate = -(attachmentRate0 + attachmentRate1)

            for i in range(len(N_He) - 1):

                nextRate = -(self.k3[i + 1] * nHe**2 * N_He[i]) + (self.kCID[i + 1] * nHe * N_He[i + 1])
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
        # self.attachment_rate_coefficients = conditions["attachment_rate_coefficients"]
        self.rateConstants = self.attachment_rate_coefficients["rateConstants"]
        self.k3 = [float(_) for _ in self.rateConstants["k3"]]
        # self.k3_branch = float(self.attachment_rate_coefficients["a(k31)"])

        self.k31_excited = self.k3_branch * self.k3[0]

        self.kCID = [float(_) for _ in self.rateConstants["kCID"]]
        self.kCID_branch = float(self.attachment_rate_coefficients["branching-ratio(kCID)"])

        self.totalAttachmentLevels = int(self.attachment_rate_coefficients["totalAttachmentLevels"])
        self.includeAttachmentRate = conditions["includeAttachmentRate"]

    def Simulate(self, nHe, duration=None, t0=0, ratio=[]):

        if not duration:
            duration = self.simulation_parameters["Simulation time(ms)"]
            duration = float(duration) * 1e-3  # converting ms ==> s

        # t0 = 0.005 if self.fixedPopulation else 0
        if duration <= t0:
            duration = t0 * 5
        tspan = [t0, duration]

        totalSteps = int(self.simulation_parameters["Total steps"])
        self.simulateTime = np.linspace(t0, duration, totalSteps)

        # Simulation start

        start_time = time.perf_counter()
        N = np.copy(self.boltzmanDistribution) if self.includeCollision else []
        N_He = self.totalAttachmentLevels * [0] if self.includeAttachmentRate else []
        ode_method = "Radau"
        options = {
            "method": ode_method,
            "t_eval": self.simulateTime,
        }

        y_init = [*N, *N_He]
        N_OFF = solve_ivp(self.SimulateODE, tspan, y_init, args=(nHe, False, self.boltzmanDistributionCold), **options)
        if self.verbose:
            logger(f"{N_OFF.nfev=} evaluations required.")
        self.lightOFF_distribution = N_OFF.y

        # Boltzmann ratio check when lightOFF
        # ratio = self.lightOFF_distribution.T[-1]
        # differenceWithBoltzman = np.around(self.boltzmanDistributionCold-ratio[:-self.totalAttachmentLevels], 3)
        # if self.verbose: logger(f"\n{ratio=}\n{self.boltzmanDistributionCold=}\n{differenceWithBoltzman=}\n")

        N_ON = solve_ivp(self.SimulateODE, tspan, y_init, args=(nHe, True, ratio), **options)

        self.lightON_distribution = N_ON.y
        if self.verbose:
            logger(f"{N_ON.nfev=} evaluations required.")

        # Ratio check after equilibrium
        # OFF_full_ratio = np.array([r/r.sum() for r in self.lightOFF_distribution[:-self.totalAttachmentLevels].T])
        # ON_full_ratio = np.array([r/r.sum() for r in self.lightON_distribution[:-self.totalAttachmentLevels].T])
        # if self.verbose: logger(f"{np.around(OFF_full_ratio[-1], 2)=}")
        # if self.verbose: logger(f"{np.around(ON_full_ratio[-1], 4)=}")
        # plt.plot(OFF_full_ratio)
        # plt.plot(ON_full_ratio)

        dataToSend = {
            "misc": {
                "ode": {"method": ode_method},
                "molecule": self.molecule,
                "tag": self.taggingPartner,
                "duration": duration,
                "numberDensity": f"{nHe:.2e}",
            },
            "legends": self.legends,
            "time (in s)": self.simulateTime.tolist(),
            "lightON_distribution": self.lightON_distribution.tolist(),
            "lightOFF_distribution": self.lightOFF_distribution.tolist(),
        }

        if self.writefile:

            name_append = f"__k3_branch_{self.k3_branch:.1f}__numberDensity_{nHe:.1e}__power_{self.power:.1e}"
            self.WriteData(name_append, dataToSend)

        end_time = time.perf_counter()

        if self.verbose:
            logger(f"Current simulation time {(end_time - start_time):.2f} s")
        if self.verbose:
            logger(f"Total simulation time {(end_time - self.start_time):.2f} s")

    def Plot(self):

        global qapp
        self.figs_location: pt = output_dir / "figs"
        if not self.figs_location.exists():
            self.figs_location.mkdir()
        widget = felionQtWindow(
            title=f"Population ratio",
            figDPI=200,
            figTitle=self.transitionTitleLabel,
            figXlabel="Time (ms)",
            figYlabel="Population",
            location=self.figs_location,
        )

        if qapp is None:
            qapp = widget.qapp

        plotSimulationTime_milliSecond: np.ndarray = self.simulateTime * 1e3
        counter = 0
        legend_handler = {}

        for on, off in zip(self.lightON_distribution, self.lightOFF_distribution):

            lg = f"{self.legends[counter]}"

            (_on_plot,) = widget.ax.plot(plotSimulationTime_milliSecond, on, ls="-", c=pltColors[counter], label=lg)
            (_off_plot,) = widget.ax.plot(plotSimulationTime_milliSecond, off, ls="--", c=pltColors[counter])

            legend_handler[lg] = _on_plot
            # legend_handler[lg] = [_on_plot, _off_plot]

            counter += 1

        widget.ax.plot(plotSimulationTime_milliSecond, self.lightON_distribution.sum(axis=0), "-k", alpha=0.5)
        widget.ax.plot(plotSimulationTime_milliSecond, self.lightOFF_distribution.sum(axis=0), "--k")

        widget.ax.hlines(
            1,
            0,
            plotSimulationTime_milliSecond[-1] + plotSimulationTime_milliSecond[-1] * 0.2,
            colors="k",
            linestyles="dashdot",
        )

        # widget.makeLegendToggler(legend_handler, edit_legend=True)

        widget.ax.legend(title="- ON -- OFF")
        widget.optimize_figure(setBound=False)
        widget.fig.tight_layout()

        if self.includeAttachmentRate:

            signal_index = len(self.energyKeys) + 1
            signal = (
                1 - (self.lightON_distribution[signal_index][1:] / self.lightOFF_distribution[signal_index][1:])
            ) * 100

            signal = np.around(np.nan_to_num(signal).clip(min=0), 1)
            widget1 = felionQtWindow(
                title=f"Signal",
                figDPI=200,
                figTitle=self.transitionTitleLabel,
                figXlabel="Time (ms)",
                figYlabel="Signal (%)",
                location=self.figs_location,
                savefilename=savefilename,
            )
            widget1.ax.plot(plotSimulationTime_milliSecond[1:], signal, label=f"Signal: {round(signal[-1])} (%)")

            if self.verbose:
                logger(f"Signal: {round(signal[-1])} (%)")
            widget1.optimize_figure(setBound=False)
            widget1.fig.tight_layout()

    def WriteData(self, name: str, dataToSend: dict):
        fulloutput_location = self.save_location or datas_location
        fulloutput_location: pt = fulloutput_location / "full_output"
        if not fulloutput_location.exists():
            fulloutput_location.mkdir()
        addText = ""
        if not includeAttachmentRate:
            addText = "__no-attachement"
        full_output_filename = f"{savefilename}{addText}__{name}.output.full.json"
        full_output_filename = remove_special_chars_in_string(full_output_filename)
        with open(fulloutput_location / full_output_filename, "w+") as f:
            data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(",", ": "))
            f.write(data)
            if self.verbose:
                logger(f"{savefilename} file written in {fulloutput_location} folder.")


figure = None
figsize = None
location = None
output_dir: pt = None
datas_location: pt = None
conditions = None
savefilename = None
includeAttachmentRate = False
fOf_appendOutputFileName = None


def main(arguments):

    global conditions, figure, savefilename, location, output_dir, datas_location, includeAttachmentRate

    conditions = arguments

    savefilename = conditions["savefilename"]
    location = pt(conditions["currentLocation"])

    output_dir = location / "output"
    if not output_dir.exists():
        output_dir.mkdir()

    datas_location = output_dir / "datas"

    if not datas_location.exists():
        datas_location.mkdir()

    figure = conditions["figure"]
    # figure["size"] = [int(i) for i in figure["size"].split(",")]

    includeAttachmentRate = conditions["includeAttachmentRate"]
    variable = conditions["variable"]

    current_nHe = float(conditions["numberDensity"])
    current_Power = float(conditions["power_broadening"]["power(W)"])
    current_k3_branch = float(conditions["attachment_rate_coefficients"]["a(k31)"])

    if variable == "time":

        ROSAA(nHe=current_nHe, power=current_Power, k3_branch=current_k3_branch, plotGraph=figure["show"], verbose=True)

    elif variable == "He density(cm-3)":

        currentConstants = {"k3_branch": [current_k3_branch, ""], "power": [current_Power, "W"]}
        functionOfVariable("numberDensity", currentConstants)

    elif variable == "Power(W)":

        currentConstants = {"k3_branch": [current_k3_branch, ""], "numberDensity": [current_nHe, "cm$^{-3}$"]}
        functionOfVariable("power", currentConstants)

    elif variable == "a(k_up/k_down)":
        currentConstants = {"power": [current_Power, "W"], "numberDensity": [current_nHe, "cm$^{-3}$"]}
        functionOfVariable("k3_branch", currentConstants)

    elif variable == "all":
        functionOfVariable("all")

    if qapp is not None:
        qapp.exec()


def make_stepsizes_equally_spaced_log(changeVariable: Literal["numberDensity", "power"]):
    variableRange: str = conditions["$variableRange"][changeVariable]

    _start, _end, _steps = variableRange.split(",")
    dataList = np.logspace(np.log10(float(_start)), np.log10(float(_end)), int(_steps), endpoint=True)

    return dataList


def functionOfVariable(
    changeVariable: Literal["numberDensity", "power", "k3_branch", "all"] = "numberDensity",
    currentConstants=None,
    plot=None,
    save_location: pt = None,
    dataList: list[float] = None,
    verbose=True,
):

    global qapp, fOf_appendOutputFileName

    if verbose:
        logger(f"Running {changeVariable} function of variable...")

    if plot is None:
        plot = figure["show"]

    if dataList is None:
        if changeVariable == "k3_branch" or changeVariable == "all":
            variableRange: str = conditions["$variableRange"]["k3_branch"]
            _start, _end, _steps = variableRange.split(",")
            dataList = np.arange(float(_start), float(_end), float(_steps))
        else:
            dataList = make_stepsizes_equally_spaced_log(changeVariable)

    if changeVariable == "all":
        simulation_time_start = time.perf_counter()
        save_folder = datas_location / "f-all"
        if not save_folder.exists():
            save_folder.mkdir()

        process_completed = 0
        power_values = make_stepsizes_equally_spaced_log("power")
        logger(f"{len(power_values)} power values to be simulated.\n{power_values=}")
        numberDensity_values = make_stepsizes_equally_spaced_log("numberDensity")
        logger(f"{len(numberDensity_values)} number density values to be simulated.\n{numberDensity_values=}")
        total_processes_count = len(dataList) * len(numberDensity_values)
        current_process_count = 0

        for _k3_branch in dataList:
            current_save_dir = save_folder / f"k3_branch_{_k3_branch:.2f}"
            if not current_save_dir.exists():
                current_save_dir.mkdir()

            logger(f"k3_branch: {_k3_branch:.2f}")
            for counter, _nHe in enumerate(numberDensity_values):

                current_process_count += 1
                functionOfVariable(
                    "power",
                    currentConstants={"k3_branch": [_k3_branch, ""], "numberDensity": [_nHe, "cm$^{-3}$"]},
                    plot=False,
                    save_location=current_save_dir,
                    dataList=power_values,
                    verbose=False,
                )
                current_variableRange = f"{power_values[0]:.2e} to {power_values[-1]:.2e}"
                logger(
                    f"{current_process_count / total_processes_count :.1%}: [a={_k3_branch:.2f}] completed {counter+1} out of {len(numberDensity_values)} cycles for power => {current_variableRange} at {_nHe:.2e} cm-3"
                )

            process_completed += 1

        simulation_time_end = time.perf_counter()
        logger(f"Total time {simulation_time_end - simulation_time_start:.2f} seconds")
        logger("Process COMPLETED")
        final_appendOutputFileName = f"f-power_{power_values[0]:.0e}-{power_values[-1]:.0e}"
        final_all_directory = current_save_dir / final_appendOutputFileName
        logger(f"Saving data to {final_all_directory}")

        # ROSAA3D_plot(final_all_directory, type="f-power")

        return

    # molecule = conditions["main_parameters"]["molecule"]
    # taggingPartner = conditions["main_parameters"]["tagging partner"]
    excitedFrom = str(conditions["excitedFrom"])
    excitedTo = str(conditions["excitedTo"])

    # outputFileName = f"{molecule}-{taggingPartner}__{excitedFrom}-{excitedTo}"

    fOf_appendOutputFileName = None
    if changeVariable == "k3_branch":
        fOf_appendOutputFileName = f"f-{changeVariable}_{dataList[0]:.2f}-{dataList[-1]:.2f}"
    elif changeVariable == "numberDensity" or changeVariable == "power":
        fOf_appendOutputFileName = f"f-{changeVariable}_{dataList[0]:.0e}-{dataList[-1]:.0e}"

    final_output_location = (save_location or datas_location) / fOf_appendOutputFileName

    if not final_output_location.exists():
        final_output_location.mkdir()

    variable_appendFileName = ""
    if isinstance(currentConstants, dict):
        for key, value in currentConstants.items():
            if key == "numberDensity" or key == "power":
                variable_appendFileName += f"_{key}_{value[0]:.1e}"
            elif key == "k3_branch":
                variable_appendFileName += f"_{key}_{value[0]:.2f}"

    outputFileName = f"{savefilename}__at_constant__{variable_appendFileName}"
    outputFileName = remove_special_chars_in_string(outputFileName)
    if verbose:
        logger(f"Output file name: {outputFileName}")

    energyKeys = list(conditions["energy_levels"].keys())

    excitedToIndex = energyKeys.index(excitedTo)
    excitedFromIndex = energyKeys.index(excitedFrom)

    populationChange = []
    signalChange = []

    for variable_counter, variable in enumerate(dataList):
        if changeVariable == "numberDensity":
            currentData = ROSAA(
                nHe=variable,
                power=currentConstants["power"][0],
                k3_branch=currentConstants["k3_branch"][0],
                save_location=final_output_location,
            )

        elif changeVariable == "power":

            currentData = ROSAA(
                nHe=currentConstants["numberDensity"][0],
                power=variable,
                k3_branch=currentConstants["k3_branch"][0],
                save_location=final_output_location,
            )

        elif changeVariable == "k3_branch":

            currentData = ROSAA(
                nHe=currentConstants["numberDensity"][0],
                power=currentConstants["power"][0],
                k3_branch=variable,
                save_location=final_output_location,
            )

        on = currentData.lightON_distribution
        changeInPopulationRatioOn = on[excitedToIndex][-1] / on[excitedFromIndex][-1]
        populationChange.append(changeInPopulationRatioOn)

        if includeAttachmentRate:
            off = currentData.lightOFF_distribution
            signal_index = len(energyKeys) + 1
            changeInSignal = (1 - (on[signal_index][-1] / off[signal_index][-1])) * 100
            changeInSignal = np.around(np.nan_to_num(changeInSignal).clip(min=0), 1)
            signalChange.append(changeInSignal)

        if verbose:
            current_variable_counter = variable_counter + 1
            logger(
                f"{current_variable_counter / len(dataList) :.1%}: completed {current_variable_counter} out of {len(dataList)} cycles for {changeVariable} => {variable:.2e}"
            )

    if plot:

        if changeVariable == "numberDensity":
            xlabel = currentData.taggingPartner + "number density (cm$^{-3})$"

        elif changeVariable == "power":
            xlabel = "Power (W)"

        elif changeVariable == "k3_branch":
            xlabel = "a (k_up / k_down)"

        title = currentData.transitionTitleLabel
        ylabel = title.split(":")[-1].replace("$", "")
        ylabel = f"${ylabel.split('-')[1]}$ / ${ylabel.split('-')[0]}$"

        widget = felionQtWindow(
            title=f"Population ratio",
            figDPI=200,
            figXlabel=xlabel,
            figYlabel=ylabel,
            location=output_dir / "figs",
            xscale="linear" if changeVariable == "k3_branch" else "log",
        )

        constantLabel = ""
        if isinstance(currentConstants, dict):
            for key, value in currentConstants.items():
                if key == "numberDensity" or key == "power":
                    constantLabel += f"{key}={value[0]:.1e} {value[1]}\n"
                elif key == "k3_branch":
                    constantLabel += f"a={value[0]:.2f} {value[1]}\n"

        widget.ax.plot(dataList, populationChange, "-k", label=constantLabel)
        widget.optimize_figure(setBound=False)
        widget.fig.tight_layout()
        if qapp is None:
            qapp = widget.qapp

    dataToSend = {
        f"variable ({changeVariable})": list(map(lambda num: np.format_float_scientific(num, 3), dataList)),
        "populationChange(up/down)": np.around(populationChange, 3).tolist(),
        "constant": currentConstants,
    }

    if includeAttachmentRate:
        if plot:
            widget1 = felionQtWindow(
                title=f"Signal",
                figDPI=200,
                figXlabel=xlabel,
                figYlabel="Signal (%)",
                location=output_dir / "figs",
                xscale="linear" if changeVariable == "k3_branch" else "log",
                savefilename=f"{outputFileName}.signal",
            )

            widget1.ax.plot(dataList, signalChange, "-k", label=constantLabel)
            widget1.optimize_figure(setBound=False)
            widget1.fig.tight_layout()

        dataToSend["signalChange"] = np.around(signalChange, 3).tolist()

    if verbose:
        logger("Compuation completed.")
    if conditions["writefile"]:
        savefileJSON = final_output_location / f"{outputFileName}.output.json"
        with open(savefileJSON, "w+") as f:
            json.dump(dataToSend, f, indent=4)
            if verbose:
                logger(f"file saved to {savefileJSON}")
                logger("Completed")
