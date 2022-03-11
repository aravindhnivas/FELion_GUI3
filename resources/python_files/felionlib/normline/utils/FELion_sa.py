
import numpy as np
from scipy.optimize import curve_fit
from .FELion_baseline_old import felix_read_file
####################################### Modules Imported #######################################
class SpectrumAnalyserCalibrator(object):
    def __init__(self, felixfile=None, fit='linear', ms=None, data=None, manual=False):
        """
        Spectrum analyser calibration initialisation
        fit can be either linear, or cubic
        """
        lowWn = 100 # discard wn below this value

        if manual: sa_x, sa_y = data
        else:
            data = felix_read_file(felixfile)
            sa_x = np.copy(data[0][np.logical_and(data[0] > lowWn, data[2] > lowWn)])
            sa_y = np.copy(data[2][np.logical_and(data[0] > lowWn, data[2] > lowWn)])

        fitType = fit=="linear"
        self.fitfunc = (lambda x, a, b, c, d: a*x**3 + b*x**2 + c*x + d, lambda x, m, c: m*x+c)[fitType]
        self.pop, poc = curve_fit(self.fitfunc, sa_x, sa_y, p0=([.01, .01, 1.0, 0.0], [1, 5])[fitType])
        if not manual: self.data = (data[0][data[2] > lowWn], data[2][data[2] > lowWn])
    def sa_cm(self, x): return self.fitfunc(x, *self.pop)
    def get_data(self): return self.data