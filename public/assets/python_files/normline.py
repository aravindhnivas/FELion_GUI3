# Importing Modules

# System modules
import sys
import json
import os
import shutil
from os.path import isdir, isfile, dirname
from pathlib import Path as pt, PurePosixPath as pt2
from itertools import cycle

# Data analysis
import numpy as np
from scipy.interpolate import interp1d

# FELion modules
from FELion_baseline_old import felix_read_file, BaselineCalibrator
from FELion_power import PowerCalibrator
from FELion_sa import SpectrumAnalyserCalibrator
from baseline import Create_Baseline
from FELion_definitions import sendData
######################################################################################

colors = [
    (31, 119, 180),
    (174, 199, 232),
    (255, 127, 14),
    (255, 187, 120),
    (44, 160, 44),
    (152, 223, 138),
    (214, 39, 40),
    (255, 152, 150),
    (148, 103, 189),
    (197, 176, 213),
    (140, 86, 75),
    (196, 156, 148),
    (227, 119, 194),
    (247, 182, 210),
    (127, 127, 127),
    (199, 199, 199),
    (188, 189, 34),
    (219, 219, 141),
    (23, 190, 207),
    (158, 218, 229),
]

def var_find(openfile):

    var = {'res': 'm03_ao13_reso', 'b0': 'm03_ao09_width',
           'trap': 'm04_ao04_sa_delay'}
    with open(openfile, 'r') as mfile:
        mfile = np.array(mfile.readlines())

    for line in mfile:
        if not len(line.strip()) == 0 and line.split()[0] == '#':
            for j in var:
                if var[j] in line.split():
                    var[j] = float(line.split()[-3])

    res, b0, trap = round(var['res'], 2), int(
        var['b0']/1000), int(var['trap']/1000)

    return res, b0, trap

class normplot:
    def __init__(self, received_files, delta, output_filename="averaged"):

        self.delta = delta
        received_files = [pt(files) for files in received_files]
        location = received_files[0].parent

        back_dir = dirname(location)
        folders = ["DATA", "EXPORT", "OUT"]
        if set(folders).issubset(os.listdir(back_dir)): 
            self.location = pt(back_dir)
        else: 
            self.location = pt(location)

        os.chdir(self.location)
        dataToSend = {"felix": {}, "base": {}, "average": {}, "SA": {}, "pow": {}, "felix_rel": {}, "average_rel": {}, "felix_per_photon": {}, "average_per_photon": {}}

        # For Average binning (Norm. method: log)
        xs = np.array([], dtype=np.float)
        ys = np.array([], dtype=np.float)

        # For Average binning (Norm. method: rel)
        xs_r = np.array([], dtype=np.float)
        ys_r = np.array([], dtype=np.float)

        c = 0
        group = 1
        color_size = len(colors)

        for filename in received_files:

            res, b0, trap = var_find(filename)
            label = f"Res:{res}; B0: {b0}ms; trap: {trap}ms"
            
            felixfile = filename.name
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

            except: self.felix_hz = 10
            self.nshots = int((trap/1000) * self.felix_hz)

            self.filetypes = [felixfile, basefile, powerfile]

            for folder, filetype in zip(folders, self.filetypes):
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
            xs = np.append(xs, wavelength)
            ys = np.append(ys, intensity)

            xs_r = np.append(xs_r, wavelength_rel)
            ys_r = np.append(ys_r, relative_depletion)

            # Wavelength and intensity of individuals with binning
            wavelength, intensity = self.felix_binning(
                wavelength, intensity)

            wavelength_rel, relative_depletion = self.felix_binning(
                wavelength_rel, relative_depletion)

            energyJ = self.inten_per_photon(wavelength, intensity)
            self.export_file(fname, wavelength, intensity, relative_depletion, energyJ, raw_intensity)

            ################### Spectrum Analyser #################################

            wn, sa = self.saCal.get_data()
            X = np.arange(wn.min(), wn.max(), 1)
            
            dataToSend["SA"][felixfile] = {
                "x": list(wn),
                "y": list(sa),
                "name": f"{filename.stem}_SA",
                "mode": "markers",
                "line": {"color": f"rgb{colors[c]}"},
                "legendgroup": f'group{group}',
            }

            dataToSend["SA"][f"{felixfile}_fit"] = {
                "x": list(X),
                "y": list(self.saCal.sa_cm(X)),
                "name": f"{filename.stem}_fit",
                "type": "scatter",
                "line": {"color": "black"},
                "showlegend": False,
                "legendgroup": f'group{group}',
            }
            
            ################### Spectrum Analyser END #################################


            ################### Averaged and Normalised Spectrum #################################

            # Normalised Intensity

            dataToSend["average"][felixfile] = {
                "x": list(wavelength),
                "y": list(intensity),
                "name": felixfile,
                "fill": 'tozeroy',
                "mode": "lines+markers",
                "line": {"color": f"rgb{colors[c]}"},
                "marker": {"size":1}
            }

            # Relative Depletion Intensity
            dataToSend["average_rel"][felixfile] = {
                "x": list(wavelength_rel),
                "y": list(relative_depletion),
                "name": felixfile,
                "fill": 'tozeroy',
                "mode": "lines+markers",
                "line": {"color": f"rgb{colors[c]}"},
                "marker": {"size":1}
            }

            # Intensitz per photon
            dataToSend["average_per_photon"][felixfile] = {
                "x": list(wavelength),
                "y": list(energyJ),
                "name": felixfile,
                "fill": 'tozeroy',
                "mode": "lines+markers",
                "line": {"color": f"rgb{colors[c]}"},
                "marker": {"size":1}
            }
            ################### Averaged Spectrum END #################################

            basefile_data = np.array(
                Create_Baseline(felixfile, self.location,
                                plotIt=False, checkdir=False, verbose=False).get_data()
            )

            # Ascending order sort by wn
            base_line = basefile_data[1][0]
            base_line = np.take(
                base_line, base_line[0].argsort(), 1).tolist()
            base_felix = basefile_data[0]
            base_felix = np.take(
                base_felix, base_felix[0].argsort(), 1).tolist()

            dataToSend["base"][f"{felixfile}_base"] = {
                "x": list(base_felix[0]),
                "y": list(base_felix[1]),
                "name": f"{felixfile}: {label}",
                "mode": "lines",
                "line": {"color": f"rgb{colors[c]}"},
                "legendgroup": f'group{group}'
            }

            dataToSend["base"][f"{felixfile}_line"] = {
                "x": list(base_line[0]),
                "y": list(base_line[1]),
                "name": f"{filename.stem}_base",
                "mode": "lines+markers",
                "marker": {"color": "black"},
                "legendgroup": f'group{group}',
                "showlegend": False,
            }

            dataToSend["pow"][powerfile] = {
                "x": list(wavelength),
                "y": list(self.total_power),
                "name": f"{powerfile}: [{self.nshots} - ({self.felix_hz}Hz)]",
                "mode": "markers",
                "xaxis": "x2",
                "yaxis": "y2",
                "marker": {"color": f"rgb{colors[c]}"},
                "legendgroup": f'group{group}',
                "showlegend": True,
            }

            group += 1
            c += 2

            if c >= color_size: c = 1

        # For Normalised Intensity
        binns, intens = self.felix_binning(xs, ys)
        dataToSend["average"]["average"] = {
            "x": list(binns),
            "y": list(intens),
            "name": "averaged",
            "mode": "lines+markers",
            "line": {"color": "black"},
            "marker": {"size":1}
        }

        # For intensityPerPhoton
        energyJ_norm = self.inten_per_photon(binns, intens)
        dataToSend["average_per_photon"]["average"] = {
            "x": list(binns),
            "y": list(energyJ_norm),
            "name": "averaged",
            "mode": "lines+markers",
            "line": {"color": "black"},
            "marker": {"size":1}
        }


        # For relative
        binns_r, intens_r = self.felix_binning(xs_r, ys_r)
        dataToSend["average_rel"]["average"] = {
            "x": list(binns_r),
            "y": list(intens_r),
            "name": "averaged",
            "mode": "lines+markers",
            "line": {"color": "black"},
            "marker": {"size":1}
        }

        # Exporting averaged.dat file
        self.export_file(f"averaged", binns, intens, intens_r, energyJ_norm)
        
        # print(f"Before JSON DATA: {dataToSend}")
        # dataJson = json.dumps(dataToSend)
        # print(dataJson)
        sendData(dataToSend)
        # print("DONE")


    def inten_per_photon(self, wn, inten): return (np.array(wn) * np.array(inten)) / 1e3

    def norm_line_felix(self, PD=True):

        felixfile, basefile, powerfile = self.filetypes

        data = felix_read_file(felixfile)
        powCal = PowerCalibrator(powerfile)
        baseCal = BaselineCalibrator(basefile)
        self.saCal = SpectrumAnalyserCalibrator(felixfile)

        wavelength = self.saCal.sa_cm(data[0])

        # self.nshots = powCal.shots(1.0)
        # self.total_power = powCal.power(data[0])*powCal.shots(data[0])
        self.power_measured = powCal.power(data[0])
        self.total_power = self.power_measured*self.nshots
        counts = data[1]
        baseCounts = baseCal.val(data[0])
        ratio = counts/baseCounts
        
        # Normalise the intensity
        # multiply by 1000 because of mJ but ONLY FOR PD!!!
        if PD:
            intensity = (-np.log(ratio)/self.total_power)*1000
        else:
            intensity = (baseCounts-counts)/self.total_power
        
        relative_depletion =(1-ratio)*100
        # relative_depletion = (baseCounts-counts)/total_power # For power normalising

        return wavelength, intensity, data[1], relative_depletion

    def export_file(self, fname, wn, inten, relative_depletion, energyPerPhoton, raw_intensity=None):

        with open('EXPORT/' + fname + '.dat', 'w+') as f:
            if raw_intensity is not None:
                f.write("#NormalisedWavelength(cm-1)\t#NormalisedIntensity\t#RelativeDepletion(%)\t#IntensityPerPhoton\t#RawIntensity\n")
                for i in range(len(wn)):
                    f.write(f"{wn[i]}\t{inten[i]}\t{relative_depletion[i]}\t{energyPerPhoton[i]}\t{raw_intensity[i]}\n")

            else:
                f.write("#NormalisedWavelength(cm-1)\t#NormalisedIntensity\t#RelativeDepletion(%)\t#IntensityPerPhoton\n")
                for i in range(len(wn)):
                    f.write(f"{wn[i]}\t{inten[i]}\t{relative_depletion[i]}\t{energyPerPhoton[i]}\n")

        expfitFile = pt(f"./EXPORT/{fname}.expfit")

        if not expfitFile.exists():
            
            with open(expfitFile, 'w+') as f:
                f.write(f"#Frequency\t#Freq_err\t#Sigma\t#Sigma_err\t#FWHM\t#FWHM_err\t#Amplitude\t#Amplitude_err\n")
            
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

if __name__ == "__main__":
    print("Argument received for normline.py: \n", sys.argv[1:][0])
    args = sys.argv[1:][0].split(",")
    print("Argument procesed:\n", args)

    filepaths = args[:-1]
    delta = float(args[-1])
    normplot(filepaths, delta)