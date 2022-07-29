import os, shutil
from os.path import isdir, isfile
from pathlib import Path as pt
import numpy as np
from .utils.FELion_baseline_old import felix_read_file, BaselineCalibrator
from .utils.FELion_power import PowerCalibrator
from .utils.FELion_sa import SpectrumAnalyserCalibrator
from felionlib.utils.FELion_definitions import sendData
from felionlib.utils.FELion_constants import colors

# from multiprocessing import Pool
######################################################################################


def var_find(openfile):

    var = {"res": "m03_ao13_reso", "b0": "m03_ao09_width", "trap": "m04_ao04_sa_delay"}

    with open(openfile, "r") as mfile:
        mfile = np.array(mfile.readlines())
    for line in mfile:
        if not len(line.strip()) == 0 and line.split()[0] == "#":
            for j in var:
                if var[j] in line.split():
                    var[j] = float(line.split()[-3])

    res, b0, trap = round(var["res"], 2), int(var["b0"] / 1000), int(var["trap"] / 1000)
    return res, b0, trap


def makeDataToSend(x, y, name, update={}):
    data = {**update, "x": list(x), "y": list(y), "name": name}
    return data


_del = "\u0394"


class normplot:
    def __init__(self, received_files, delta):

        self.delta = delta
        self.received_files = [pt(files) for files in received_files]
        location = self.received_files[0].parent
        # back_dir = location.parent

        self.folders = ["DATA", "EXPORT", "OUT"]

        if set(self.folders).issubset(os.listdir(location.parent)):
            self.location = pt(location.parent)
        else:
            self.location = pt(location)
        os.chdir(self.location)

        self.dataToSend = {"SA": {}, "pow": {}, "base": {}, "average": {}, "average_rel": {}, "average_per_photon": {}}

        # For Average binning (Norm. method: log)
        self.xs = np.array([], dtype=float)
        self.ys = np.array([], dtype=float)
        self.xs_r = np.array([], dtype=float)
        self.ys_r = np.array([], dtype=float)
        self.group = 1
        self.colorIndex = 0
        self.colorSize = len(colors)

    def begin_compute(self):

        percent_completed = 0
        for counter, filename in enumerate(self.received_files):
            self.compute(filename)
            print("computing", filename.name, flush=True)
            percent_completed = (counter+1) / len(self.received_files) * 100
            print(f"{percent_completed:.2f}% completed", flush=True)

        # For Normalised Intensity
        binns, intens = self.felix_binning(self.xs, self.ys)
        energyJ_norm = self.inten_per_photon(binns, intens)
        binns_r, intens_r = self.felix_binning(self.xs_r, self.ys_r)

        defaultStyle = {"mode": "lines+markers", "marker": {"size": 1}, "line": {"color": "black", "shape": "hv"}}
        felixfile_avg_lg = f"averaged({_del}: {round(np.diff(binns).mean(), 1)})"
        self.dataToSend["average"]["average"] = makeDataToSend(binns, intens, felixfile_avg_lg, update=defaultStyle)

        self.dataToSend["average_rel"]["average"] = makeDataToSend(
            binns_r, intens_r, felixfile_avg_lg, update=defaultStyle
        )
        self.dataToSend["average_per_photon"]["average"] = makeDataToSend(
            binns, energyJ_norm, felixfile_avg_lg, update=defaultStyle
        )

        self.export_file(f"averaged", binns, intens, intens_r, energyJ_norm)

    def save_data_to_temp_file(self):
        sendData(self.dataToSend, calling_file=pt(__file__).stem)

    def compute(self, filename):

        felixfile = filename.name
        res, b0, trap = var_find(filename)

        label = f"{felixfile}; Res:{res}; B0: {b0}ms; trap: {trap}ms"

        fname = filename.stem
        basefile = f"{fname}.base"
        powerfile = f"{fname}.pow"

        try:
            with open(f"./DATA/{powerfile}") as f:
                for line in f:
                    if line[0] == "#":
                        if line.find("Hz") > -1:
                            felix_hz = int(line.split(" ")[1])
                            break
            self.felix_hz = int(felix_hz)

        except Exception as error:
            print(error, flush=True)
            self.felix_hz = 10

        print(f"read: {trap=}", flush=True)

        if trap / 1000 > 5:
            with open(f"./DATA/{powerfile}") as f:
                try:
                    for line in f:
                        if line[0] == "#":
                            if line.find("SHOTS") > -1:
                                nshots = int(line.split("=")[1].strip())
                                break
                    self.nshots = int(nshots)

                except Exception as error:
                    print(error, flush=True)
                    raise Exception(error)
        else:

            self.nshots = int((trap / 1000) * self.felix_hz)

        self.filetypes = [felixfile, basefile, powerfile]

        for folder, filetype in zip(self.folders, self.filetypes):

            if not isdir(folder):
                os.mkdir(folder)

            if isfile(filetype):
                shutil.move(
                    self.location.joinpath(filetype),
                    self.location.joinpath("DATA", filetype),
                )

        # Wavelength and intensity of individuals without binning
        wavelength, intensity, raw_intensity, relative_depletion = self.norm_line_felix()

        wavelength_rel = np.copy(wavelength)

        # collecting Wavelength and intensity to average spectrum with binning

        self.xs = np.append(self.xs, wavelength)
        self.ys = np.append(self.ys, intensity)

        self.xs_r = np.append(self.xs_r, wavelength_rel)
        self.ys_r = np.append(self.ys_r, relative_depletion)

        energyJ = self.inten_per_photon(wavelength, intensity)
        self.export_file(fname, wavelength, intensity, relative_depletion, energyJ, raw_intensity)

        ################### Spectrum Analyser #################################
        wn, sa = self.saCal.get_data()
        X = np.arange(wn.min(), wn.max(), 1)

        lineColor = {"color": f"rgb{colors[self.colorIndex]}", "shape": "hv"}
        blackColor = {"color": "black"}
        groupItem = {"legendgroup": f"group{self.group}"}
        nolegend = {"showlegend": False}

        self.dataToSend["SA"][felixfile] = makeDataToSend(
            wn, sa, f"{filename.stem}_SA", update={"line": lineColor, **groupItem, "mode": "markers"}
        )
        self.dataToSend["SA"][f"{felixfile}_fit"] = makeDataToSend(
            X,
            self.saCal.sa_cm(X),
            f"{filename.stem}_fit",
            update={"mode": "lines", "line": blackColor, **groupItem, **nolegend},
        )

        powlegend = f"{powerfile}: [{self.nshots} - ({self.felix_hz} Hz)]"
        self.dataToSend["pow"][powerfile] = makeDataToSend(
            wavelength,
            self.total_power,
            powlegend,
            update={"mode": "markers", "xaxis": "x2", "yaxis": "y2", "marker": lineColor, **groupItem},
        )

        ################### Spectrum Analyser END #################################
        ################### Averaged and Normalised Spectrum #################################

        # Normalised Intensity

        defaultStyle = {"mode": "lines+markers", "fill": "tozeroy", "marker": {"size": 1}, "line": lineColor}

        felixfile_lg = f"{felixfile}({_del}:{round(np.diff(wavelength).mean(), 1)})"

        self.dataToSend["average"][felixfile] = makeDataToSend(wavelength, intensity, felixfile_lg, update=defaultStyle)

        self.dataToSend["average_rel"][felixfile] = makeDataToSend(
            wavelength_rel, relative_depletion, felixfile_lg, update=defaultStyle
        )

        self.dataToSend["average_per_photon"][felixfile] = makeDataToSend(
            wavelength, energyJ, felixfile_lg, update=defaultStyle
        )

        ################### Averaged Spectrum END #################################

        base_line = np.genfromtxt(self.location / f"DATA/{basefile}").T

        base_line = np.take(base_line, base_line[0].argsort(), 1)

        self.dataToSend["base"][f"{felixfile}_base"] = makeDataToSend(
            self.data[0], self.data[1], label, update={"mode": "lines", "line": lineColor, **groupItem}
        )

        self.dataToSend["base"][f"{felixfile}_line"] = makeDataToSend(
            base_line[0],
            base_line[1],
            felixfile,
            update={"mode": "lines+markers", "line": blackColor, **groupItem, **nolegend},
        )

        self.group += 1
        self.colorIndex += 2

        if self.colorIndex >= self.colorSize:
            self.colorIndex = 1

    def inten_per_photon(self, wn, inten):
        return (np.array(wn) * np.array(inten)) / 1e3

    def norm_line_felix(self, PD=True):

        felixfile, basefile, powerfile = self.filetypes

        self.data = felix_read_file(felixfile)
        powCal = PowerCalibrator(powerfile)

        baseCal = BaselineCalibrator(basefile)

        self.saCal = SpectrumAnalyserCalibrator(felixfile)

        wavelength = self.saCal.sa_cm(self.data[0])

        self.power_measured = powCal.power(self.data[0])
        self.total_power = self.power_measured * self.nshots

        counts = self.data[1]
        baseCounts = baseCal.val(self.data[0])
        ratio = counts / baseCounts

        self.sa_diff = np.diff((self.data[2] - self.data[1])).mean()
        # print(f"Spectrum analyser is {self.sa_diff } more than set wn.")

        # Normalise the intensity
        # multiply by 1000 because of mJ but ONLY FOR PD!!!
        if PD:
            intensity = (-np.log(ratio) / self.total_power) * 1000
        else:
            intensity = (baseCounts - counts) / self.total_power
        relative_depletion = (1 - ratio) * 100
        return wavelength, intensity, self.data[1], relative_depletion

    def export_file(self, fname, wn, inten, relative_depletion, energyPerPhoton, raw_intensity=None):

        with open("EXPORT/" + fname + ".dat", "w+") as f:

            fileInfo = None
            if fname == "averaged":
                fileInfo = [_.name for _ in self.received_files]
                fileInfo = f"# {fileInfo}\n#########################################\n\n"
            unitInfo = f"# cm-1\tNorm. Int./J\t%\tNorm. Int./photon\n"
            if raw_intensity is not None:
                f.write(
                    "#NormalisedWavelength(cm-1)\t#NormalisedIntensity\t#RelativeDepletion(%)\t#IntensityPerPhoton\t#RawIntensity\n"
                )
                f.write(unitInfo)
                if fileInfo is not None:
                    f.write(fileInfo)
                for i in range(len(wn)):
                    f.write(f"{wn[i]}\t{inten[i]}\t{relative_depletion[i]}\t{energyPerPhoton[i]}\t{raw_intensity[i]}\n")
            else:
                f.write(
                    "#NormalisedWavelength(cm-1)\t#NormalisedIntensity\t#RelativeDepletion(%)\t#IntensityPerPhoton\n"
                )
                f.write(unitInfo)
                if fileInfo is not None:
                    f.write(fileInfo)

                for i in range(len(wn)):
                    f.write(f"{wn[i]}\t{inten[i]}\t{relative_depletion[i]}\t{energyPerPhoton[i]}\n")

    def felix_binning(self, xs, ys):

        delta = self.delta
        """
        Binns the data provided in xs and ys to bins of width delta
        output: binns, intensity 
        """

        # bins = np.arange(start, end, delta)
        # occurance = np.zeros(start, end, delta)
        BIN_STEP = delta
        BIN_START = xs.min()
        BIN_STOP = xs.max()

        indices = xs.argsort()
        datax = xs[indices]
        datay = ys[indices]

        # print("In total we have: ", len(datax), ' data points.')
        # do the binning of the data
        bins = np.arange(BIN_START, BIN_STOP, BIN_STEP)
        # print("Binning starts: ", BIN_START,
        #    ' with step: ', BIN_STEP, ' ENDS: ', BIN_STOP)

        bin_i = np.digitize(datax, bins)
        bin_a = np.zeros(len(bins) + 1)
        bin_occ = np.zeros(len(bins) + 1)

        for i in range(datay.size):
            bin_a[bin_i[i]] += datay[i]
            bin_occ[bin_i[i]] += 1

        binsx, data_binned = [], []
        for i in range(bin_occ.size - 1):
            if bin_occ[i] > 0:
                binsx.append(bins[i] - BIN_STEP / 2)
                data_binned.append(bin_a[i] / bin_occ[i])

        # non_zero_i = bin_occ > 0
        # binsx = bins[non_zero_i] - BIN_STEP/2
        # data_binned = bin_a[non_zero_i]/bin_occ[non_zero_i]

        return binsx, data_binned

    def powerfileInfo(self, powerfile):
        with open(f"./DATA/{powerfile}") as f:
            for line in f:
                if line[0] == "#":
                    if line.find("Hz") == 1:
                        return int(line.split(" ")[1])


def main(args):
    print(f"felix: {args=}")
    
    felixfiles = args["felixfiles"]
    delta = float(args["delta"])
    
    Normplot = normplot(felixfiles, delta)
    Normplot.begin_compute()
    # Normplot.save_data_to_temp_file()
    return Normplot.dataToSend
    