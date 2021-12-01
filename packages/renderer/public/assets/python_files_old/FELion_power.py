import numpy as np
from scipy.interpolate import interp1d

####################################### Modules Imported #######################################
class PowerCalibrator(object):

    def __init__(self, powerfile, ms=None):
 
        self.n_shots = 1
        self.interpol = 'linear'
        in_um = False
        xw, yw = [],[]
        with open(f'./DATA/{powerfile}') as f:
            for line in f:
                if line[0] == '#':
                    if line.find('SHOTS')>-1:
                        self.n_shots = float(line.split('=')[-1])
                    if line.find('IN_UM')>-1:
                        in_um = True
                    if line.find('INTERP')>-1:
                        self.interpol = line.split('=')[-1].strip('\n')
                    continue
                else:
                    if not line == "\n":
                        x, y, = line.split()
                        xw.append(float(x))
                        yw.append(float(y))
        
            if in_um:
                self.xw = 10000/np.array(xw)
            else:
                self.xw = np.array(xw)

            self.yw = np.array(yw)
        
        self.f = interp1d(self.xw, self.yw, kind=self.interpol, fill_value='extrapolate')


    def power(self, x):
        return self.f(x) 

    def shots(self, x):
        if type(x)==float:
            return self.n_shots 
        else:
            return np.zeros(len(x)) + self.n_shots