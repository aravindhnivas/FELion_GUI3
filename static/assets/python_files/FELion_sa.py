
import numpy as np
from scipy.optimize import leastsq, curve_fit
from FELion_baseline_old import felix_read_file
####################################### Modules Imported #######################################
class SpectrumAnalyserCalibrator(object):
    def __init__(self, felixfile=None, fit='linear', ms=None, data=None, manual=False):
        """
        Spectrum analyser calibration initialisation
        fit can be either linear, or cubic
        """
        # self.ms = ms

        lowWn = 100 # discard wn below this value

        if manual: sa_x, sa_y = data

        else:
            data = felix_read_file(felixfile)
            sa_x = np.copy(data[0][np.logical_and(data[0] > lowWn, data[2] > lowWn)])
            sa_y = np.copy(data[2][np.logical_and(data[0] > lowWn, data[2] > lowWn)])

        fitType = fit=="linear"
        self.fitfunc = (lambda x, a, b, c, d: a*x**3 + b*x**2 + c*x + d, lambda x, m, c: m*x+c)[fitType]
        self.pop, poc = curve_fit(self.fitfunc, sa_x, sa_y, p0=([.01, .01, 1.0, 0.0], [1, 5])[fitType])

        print(f"Spectrum Analyser: Fitted - {fit}\nParameters: {self.pop}")

        # if fit == 'linear':
        #     p0 = [1.0, 5.0]
        #     def fitfunc(p, x): return p[0]*x + p[1]

        # elif fit == 'cubic':

        #     p0 = [.01, .01, 1.0, 0.0]
        #     def fitfunc(p, x): return p[0]*x**3 + p[1]*x**2 + p[2]*x + p[3]
        # else: print("SA fitting function not defined!!!")

        # def errfunc(p, x, y): return (fitfunc(p, x)-y)

        # p, cov_p, info, mesg, ier \
        #     = leastsq(errfunc, p0, args=(sa_x, sa_y), full_output=1)

        # if ier not in [1, 2, 3, 4] or cov_p is None:
        #     msg = "SA calibration optimal parameters not found: " + mesg
        #     raise RuntimeError(msg)
        # if any(np.diag(cov_p) < 0):
        #     raise RuntimeError( "Optimal parameters not found: negative variance")

        # chisq = np.dot(info["fvec"], info["fvec"])
        # dof = len(info["fvec"]) - len(p)
        # sigma = np.array([np.sqrt(cov_p[i, i])*np.sqrt(chisq/dof)
        #                   for i in range(len(p))])

        # self.p = p
        # self.sigma = sigma
        # self.f = fitfunc
        # print(self.p)
        if not manual: self.data = (data[0][data[2] > lowWn], data[2][data[2] > lowWn])

    def sa_cm(self, x): return self.fitfunc(x, *self.pop)

    def get_data(self): return self.data