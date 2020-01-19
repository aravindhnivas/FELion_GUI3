
# Importing Modules

# System modules
import sys, json, os
from os.path import isdir, isfile
from pathlib import Path as pt

# Data analysis
import numpy as np
from uncertainties import unumpy as unp


####################################### Modules Imported #######################################

class timescanplot:

    def __init__(self, scanfile):

        location = scanfile.parent

        os.chdir(location)
        skip = get_skip_line(scanfile.name, location)
        iterations = get_iterations(scanfile.name, location)

        # opening File
        data = np.genfromtxt(scanfile, skip_header=skip)

        cycle = int(len(data)/iterations.sum())
        run = len(iterations)
        time = data[:, 1][: cycle] # in ms

        # Calculating mean and std_devs
        j, mass_count = 0, 0
        mean, error, mass, m = [], [], [], {}
        t_res, t_b0 = var_find(scanfile, location, time=True)

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

            m[f"{mass_value}u"] = {"x":list(time), "y":list(mass_sort), 
                    "name": f"{mass_value}u[{iteration}]; B0:{t_b0}ms; Res: {t_res}", "mode": 'lines+markers',
                    "error_y":{"type": "data","array": list(error_sort),"visible": True}}

            j = k + j

        mean = mean.reshape(run, cycle)
        error = error.reshape(run, cycle)

        m["SUM"] = {"x":list(time), "y":list(mean.sum(axis=0)), 
                        "name": f"SUM", "mode": 'lines+markers', "line":{"color":"black"},
                        "error_y":{"type": "data","array": list(error.sum(axis=0)),"visible": True}}

        dataJson = json.dumps(m)

        self.m = m

        # print(dataJson)
        
        self.time, self.mean, self.error, self.mass, self.t_res, self.t_b0 = time, mean, error, mass, t_res, t_b0

    def get_data(self): return self.time, self.mean, self.error, self.mass, self.t_res, self.t_b0
    def get_fullmass(self): return self.m


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
    filepaths = [pt(i) for i in args]
    # location = filepaths[0].parent

    timescanplot(filepaths[0])