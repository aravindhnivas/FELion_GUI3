from FELion_widgets import FELion_Tk
from FELion_definitions import sendData
import traceback
from pathlib import Path as pt
import warnings
import numpy as np
from uncertainties import unumpy as unp
import json

warnings.simplefilter(action='ignore', category=FutureWarning)

class timescanplot:

    def __init__(self, scanfile, tkplot=False):
        self.scanfile = pt(scanfile)
        self.location = scanfile.parent

        if tkplot:

            self.widget = FELion_Tk(title=scanfile, location=scanfile.parent)

            self.fig, self.canvas = self.widget.Figure(default_save_widget=False)
            self.widget.save_fmt = self.widget.Entries("Entry", "png", 0.1, 0.05*9+0.02)
            self.widget.save_btn = self.widget.Buttons("Save", 0.5, 0.05*9, self.widget.save_fig)
            savename=self.scanfile.stem
            ax = self.widget.make_figure_layout(title=f"Timescan: {self.scanfile.name}", xaxis="Time (ms)", yaxis="Counts", yscale="linear", savename=savename)
            
            self.widget.lines = {}

            self.read_timescan_file(ax=ax)
            self.widget.lines["SUM"] = ax.errorbar(self.time, self.mean.sum(axis=0), yerr=self.error.sum(axis=0), label="SUM", fmt="k.-")
            self.widget.plot_legend = ax.legend()
            self.widget.mainloop()
        else:
            self.read_timescan_file(tkplot=False)
            
    def get_data(self): return self.time, self.mean, self.error, self.mass, self.t_res, self.t_b0
    def get_plotly_data(self): return self.m
        
    def read_timescan_file(self, ax=None, tkplot=True):

        m={}
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
            mass_value = float(data[:, 0][j:k+j][0])
            print(mass_value, type(mass_value))
            if mass_value in mass:
                mass_count += 1
                mass_value = f'{mass_value}_{mass_count}'
            mass_sort = data[:, 2][j:k + j].reshape(iteration, cycle).mean(axis=0)
            error_sort = data[:, 2][j:k + j].reshape(iteration, cycle).std(axis=0)

            mass.append(mass_value)
            mean = np.append(mean, mass_sort)
            error = np.append(error, error_sort)
            label = f"{mass_value}u[{iteration}]:{t_b0}ms[{t_res}V]"

            if tkplot: 
                print(f"{mass_value}: error value:\n{error_sort}")
                self.widget.lines[f"{mass_value}"] = ax.errorbar(time, mass_sort, yerr=error_sort, label=label, fmt=".-")

            else:
                m[f"{mass_value}u"] = {"x":time.tolist(), "y":mass_sort.tolist(), 
                        "name": label, "mode": 'lines+markers',
                        "error_y":{"type": "data","array": error_sort.tolist(),"visible": True}}
            j = k + j

        self.mass = mass
        mean = mean.reshape(run, cycle)
        error = error.reshape(run, cycle)

        self.time, self.mean, self.error = time, mean, error
        m["SUM"] = {"x":time.tolist(), "y":mean.sum(axis=0).tolist(), "name": f"SUM", "mode": 'lines+markers', "line":{"color":"black"},
            "error_y":{"type": "data", "array": error.sum(axis=0).tolist(),"visible": True}}

        self.m = m

def var_find(fname, location, time=False):

    if fname != '':
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
    with open(location/scanfile, 'r') as f:
        skip = 0
        for line in f:
            if len(line) > 1:
                line = line.strip()
                if line == 'ALL:':
                    return skip + 1
            skip += 1
    return f'ALL: is not found in the file'

def get_iterations(scanfile, location):
    
    iterations = np.array([])
    
    with open(location/scanfile, 'r') as f:
        for line in f:
    
            if line.startswith('#mass'):
                iterations = np.append(iterations, line.split(':')[-1]).astype(np.int64)
            else:
                continue
    return iterations

def main(args):
    scanfiles = [pt(i) for i in args["scanfiles"]]

    location = scanfiles[0].parent
    EXPORT_DIR = location / "EXPORT"
    if not EXPORT_DIR.exists(): EXPORT_DIR.mkdir()
    
    tkplot = args["tkplot"]
    if tkplot == "plot": 
        timescanplot(scanfiles[0], tkplot=True)
    else:
    
        dataToSend = {}
        for i in scanfiles:
            
            data = timescanplot(i)
            filename = i.name
            dataToSend[filename] = data.get_plotly_data()
            
            try:
                
                with open(EXPORT_DIR / f"{i.stem}_scan.json", 'w+') as f:
                    data = json.dumps(dataToSend[filename], sort_keys=True, indent=4, separators=(',', ': '))
                    f.write(data)
            except:
                print("Couldn't write file to EXPORT directory")
                
        sendData(dataToSend, calling_file=pt(__file__).stem)