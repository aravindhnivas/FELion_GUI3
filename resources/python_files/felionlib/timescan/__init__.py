
import json
from typing import Any, Union
import warnings
from pathlib import Path as pt
import numpy as np
from felionlib.utils.FELion_definitions import sendData
warnings.simplefilter(action='ignore', category=FutureWarning)
from felionlib.utils.felionQt import felionQtWindow, QApplication
from .utils import var_find, get_iterations, get_skip_line

class timescanplot:

    def __init__(self, scanfile: Union[str, pt]):
        
        self.scanfile = pt(scanfile)
        self.location: pt = scanfile.parent

    def create_QtFigure(self):
        
        qapp = QApplication([])

        self.widget = felionQtWindow(
            figXlabel="Time (ms)", figYlabel="Counts",
            location=self.location/"OUT", savefilename=self.scanfile.stem
        )
        self.legend_handler = {}

        self.compute_data(tkplot=True)
        
        self.legend_handler["SUM"] = self.widget.ax.errorbar(
            self.time, self.mean.sum(axis=0), 
            yerr=self.error.sum(axis=0), label="SUM", fmt="k.-"
        )

        self.widget.optimize_figure()
        self.widget.fig.tight_layout()
        self.widget.makeLegendToggler(self.legend_handler)

        qapp.exec()
   
    # def get_data(self): return self.time, self.mean, self.error, self.mass, self.t_res, self.t_b0
    # def get_plotly_data(self): return self.m
    
    def compute_data(self, tkplot=False):

        self.plotly_data={}
        location = self.scanfile.parent

        skip = get_skip_line(self.scanfile.name, location)
        iterations = get_iterations(self.scanfile.name, location)

        # opening File
        data: np.ndarray = np.genfromtxt(self.scanfile, skip_header=skip)

        cycle = int(len(data)/iterations.sum())
        run = len(iterations)
        self.time: np.ndarray = data[:, 1][:cycle] # in ms

        # Calculating mean and std_devs
        j, mass_count = 0, 0
        
        self.mean, self.error, self.mass = [], [], []
        self.t_res, self.t_b0 = var_find(self.scanfile)

        for iteration in iterations:
            
            k: int = iteration*cycle
            
            mass_value = float(data[:, 0][j:k+j][0])
            
            if mass_value in self.mass:
                mass_count += 1
                mass_value = f'{mass_value}_{mass_count}'

            mass_sort: np.ndarray = data[:, 2][j:k + j]
            mass_sort = mass_sort.reshape(iteration, cycle).mean(axis=0)
            
            error_sort: np.ndarray = data[:, 2][j:k + j]
            error_sort = error_sort.reshape(iteration, cycle).std(axis=0)

            self.mass.append(mass_value)
            self.mean: np.ndarray = np.append(self.mean, mass_sort)
            self.error: np.ndarray = np.append(self.error, error_sort)
            label: str = f"{mass_value}u[{iteration}]:{self.t_b0}ms[{self.t_res}V]"

            if tkplot: 
                self.legend_handler[label] = self.widget.ax.errorbar(
                    self.time, mass_sort, yerr=error_sort, label=label, fmt=".-"
                )

            self.plotly_data[f"{mass_value}u"] = {
                "x": self.time.tolist(), "y": mass_sort.tolist(), 
                "name": label, "mode": 'lines+markers',
                "error_y": {"type": "data","array": error_sort.tolist(), "visible": True}
            }
            j = k + j

        # self.mass = mass

        self.mean = self.mean.reshape(run, cycle)
        self.error = self.error.reshape(run, cycle)

        # self.time, self.mean, self.error = time, mean, error
        
        self.plotly_data["SUM"] = {
            "x": self.time.tolist(), "y": self.mean.sum(axis=0).tolist(),
            "name": f"SUM", "mode": 'lines+markers',
            "line": {"color":"black"},
            "error_y": {"type": "data", "array": self.error.sum(axis=0).tolist(), "visible": True}
        }


def main(args):
    
    scanfiles = [pt(i) for i in args["scanfiles"]]
    location = scanfiles[0].parent
    
    EXPORT_DIR = location / "EXPORT"
    if not EXPORT_DIR.exists(): EXPORT_DIR.mkdir()

    tkplot = args["tkplot"]

    if tkplot == "plot": 
        data = timescanplot(scanfiles[0])
        data.create_QtFigure()

    else:
        dataToSend = {}
        for i in scanfiles:
            data = timescanplot(i)
            data.compute_data()
            filename = i.name
            dataToSend[filename] = data.plotly_data
            
            try:
                with open(EXPORT_DIR / f"{i.stem}_scan.json", 'w+') as f:
                    data = json.dumps(dataToSend[filename], sort_keys=True, indent=4, separators=(',', ': '))
                    f.write(data)
                print("Files are saved", flush=True)
            except:
                print("Couldn't write file to EXPORT directory")
        sendData(dataToSend, calling_file=pt(__file__).stem)
