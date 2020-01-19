
# FELion tkinter figure module
from FELion_widgets import FELion_Tk
from FELion_definitions import sendData
from tkinter.messagebox import askokcancel, showerror
# System modules
import sys, json, os, traceback
from os.path import isdir, isfile
from pathlib import Path as pt

# Data analysis
import numpy as np
from uncertainties import unumpy as unp

# from matplotlib import style
import matplotlib.pyplot as plt
class timescanplot:

    def __init__(self, scanfile, tkplot=False):

        self.scanfile = scanfile = pt(scanfile)
        self.location = location = scanfile.parent
        os.chdir(location)

        if tkplot:

            self.widget = FELion_Tk(title=scanfile, location=scanfile.parent)

            self.fig, self.canvas = self.widget.Figure(default_save_widget=False)
            self.widget.save_fmt = self.widget.Entries("Entry", "png", 0.1, 0.05*9+0.02)
            self.widget.save_btn = self.widget.Buttons("Save", 0.5, 0.05*9, self.savefig_timescan)
            savename=scanfile.stem
            ax = self.widget.make_figure_layout(title=f"Timescan: {scanfile.name}", xaxis="Time (ms)", yaxis="Counts", yscale="linear", savename=savename)
            self.widget.lines = {}

        if tkplot:

            time, mean, error = self.read_timescan_file(ax=ax)
            self.widget.lines["SUM"] = ax.errorbar(time, mean.sum(axis=0), yerr=error.sum(axis=0), label="SUM", fmt="k.-")
            self.widget.plot_legend = ax.legend()
            self.widget.mainloop()

        else:

            m = {}
            time, mean, error = self.read_timescan_file(tkplot=False, m=m)
            m["SUM"] = {"x":list(time), "y":list(mean.sum(axis=0)), 
                            "name": f"SUM", "mode": 'lines+markers', "line":{"color":"black"},
                            "error_y":{"type": "data","array": list(error.sum(axis=0)),"visible": True}}
            
            sendData(m)

        self.time, self.mean, self.error = time, mean, error

    def get_data(self): return self.time, self.mean, self.error, self.mass, self.t_res, self.t_b0

    def savefig_timescan(self):

        save_fname = f"{self.widget.name.get()}.{self.widget.save_fmt.get()}"
        print(f"Saving filename: {save_fname}")
        save_filename = self.location / save_fname

        if not self.widget.latex.get(): self.widget.save_fig()

        else:
            style_path = pt(__file__).parent / "matplolib_styles/styles/science.mplstyle"

            with plt.style.context([f"{style_path}"]):

                fig, ax = plt.subplots()

                time, mean, error = self.read_timescan_file(ax=ax)
                ax.errorbar(time, mean.sum(axis=0), yerr=error.sum(axis=0), label="SUM", fmt="k.-")

                ax.grid(self.widget.plotGrid.get())

                legend = ax.legend(bbox_to_anchor=[1, 1], fontsize=self.widget.xlabelSz.get()/2)
                legend.set_visible(self.widget.plotLegend.get())

                # Setting title
                ax.set_title(self.widget.plotTitle.get().replace("_", "\_"), fontsize=self.widget.titleSz.get())

                # Setting X and Y label
                if self.widget.plotYscale.get(): scale = "log"
                else: scale = "linear"
                ax.set(yscale=scale)
                ax.set(
                    ylabel=self.widget.plotYlabel.get().replace("%", "\%"), 
                    xlabel=self.widget.plotXlabel.get()
                )

                # Xlabel and Ylabel fontsize
                ax.xaxis.label.set_size(self.widget.xlabelSz.get())
                ax.yaxis.label.set_size(self.widget.ylabelSz.get())
                ax.tick_params(axis='x', which='major', labelsize=self.widget.xlabelSz.get())
                ax.tick_params(axis='y', which='major', labelsize=self.widget.ylabelSz.get())

                try:
                    fig.savefig(save_filename, dpi=self.widget.dpi_value.get()*2)
                    print(f"File saved:\n{save_filename}")
                    if askokcancel('Open savedfile?', f'File: {save_fname}\nsaved in directory: {self.location}'):
                        print("Opening file: ", save_filename)
                        os.system(f"{save_filename}")
                except: showerror("Error", traceback.format_exc(5))
                
    def read_timescan_file(self, ax=None, tkplot=True, m=None):

        location = self.scanfile.parent

        skip = get_skip_line(self.scanfile.name, location)
        iterations = get_iterations(self.scanfile.name, location)

        # opening File
        data = np.genfromtxt(self.scanfile, skip_header=skip)

        cycle = int(len(data)/iterations.sum())
        run = len(iterations)
        time = data[:, 1][: cycle] # in ms

        # Calculating mean and std_devs
        j, mass_count = 0, 0
        mean, error, mass = [], [], []

        t_res, t_b0 = var_find(self.scanfile, location, time=True)
        self.t_res, self.t_b0 = t_res, t_b0
        self.timedata = {"mass_value":[], "time":[], "Counts":[], "error":[], "SUM":[], "SUM_error":[]}

        for iteration in iterations:
            
            k = iteration*cycle
            mass_value = data[:, 0][j:k+j][0]

            if mass_value in mass:
                mass_count += 1
                mass_value = f'{mass_value}_{mass_count}'

            mass_sort = data[:, 2][j:k + j].reshape(iteration, cycle).mean(axis=0)
            error_sort = data[:, 2][j:k + j].reshape(iteration, cycle).std(axis=0)

            mass = np.append(mass, mass_value)
            mean = np.append(mean, mass_sort)
            error = np.append(error, error_sort)

            label = f"{mass_value}u[{iteration}]:{t_b0}ms[{t_res}V]"

            if tkplot: 
                print(f"{mass_value}: error value:\n{error_sort}")
                self.widget.lines[f"{mass_value}"] = ax.errorbar(time, mass_sort, yerr=error_sort, label=label, fmt=".-")

            else:
                m[f"{mass_value}u"] = {"x":list(time), "y":list(mass_sort), 
                        "name": label, "mode": 'lines+markers',
                        "error_y":{"type": "data","array": list(error_sort),"visible": True}}

            j = k + j
        self.mass = mass
        mean = mean.reshape(run, cycle)
        error = error.reshape(run, cycle)

        return time, mean, error

def var_find(fname, location, time=False):

    if not fname is '':
        
        os.chdir(location)
        if not time:
            var = {'res': 'm03_ao13_reso', 'b0': 'm03_ao09_width',
                   'trap': 'm04_ao04_sa_delay'}
        else:
            var = {'res': 'm03_ao13_reso', 'b0': 'm03_ao09_width'}

        with open(fname, 'r') as f:
            f = np.array(f.readlines())
        for i in f:
            if not len(i.strip()) == 0 and i.split()[0] == '#':
                for j in var:
                    if var[j] in i.split():
                        var[j] = float(i.split()[-3])

        if not time:
            res, b0, trap = round(var['res'], 1), int(
                var['b0']/1000), int(var['trap']/1000)
        else:
            res, b0 = round(var['res'], 1), int(var['b0']/1000)

        if time:
            return res, b0

        return res, b0, trap
    
    else:
        if time:
            return 0, 0
        return 0, 0, 0

def get_skip_line(scanfile, location):
    ##print("\nGetting skip line\n")

    os.chdir(location)
    with open(scanfile, 'r') as f:
        skip = 0
        for line in f:
            if len(line) > 1:
                line = line.strip()
                if line == 'ALL:':
                    #print(f'\n{line} found at line no. {skip+1}\n')
                    return skip + 1
            skip += 1
    return f'ALL: is not found in the file'

def get_iterations(scanfile, location):

    os.chdir(location)
    iterations = np.array([])
    with open(scanfile, 'r') as f:
        for line in f:
            if line.startswith('#mass'):
                #print(line)
                iterations = np.append(
                    iterations, line.split(':')[-1]).astype(np.int64)
            else:
                continue
    return iterations


if __name__ == "__main__":
    
    args = sys.argv[1:][0].split(",")
    filename = args[0]

    tkplot = args[-1]
    if tkplot == "plot": timescanplot(filename, tkplot=True)
    else: timescanplot(filename)