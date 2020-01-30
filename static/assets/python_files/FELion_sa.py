import numpy as np
from scipy.optimize import leastsq
from FELion_baseline_old import felix_read_file

####################################### Modules Imported #######################################

class SpectrumAnalyserCalibrator(object):
    def __init__(self, felixfile, fit='linear', ms=None):
        """
        Spectrum analyser calibration initialisation
        fit can be either linear, or cubic
        """

        self.ms = ms

        data = felix_read_file(felixfile)

        # Spectrum analyser calibration
        # Added 6.10.16:
        # Spectrum analyser is calibrated only above 540 cm-1, because for lower values SA gives bulshit values!
        # In case, someone does not follow the SA, value of SA < 100 will get also excluded from the fit!!!!
        sa_x = np.copy(data[0][np.logical_and(data[0] > 100, data[2] > 100)])
        sa_y = np.copy(data[2][np.logical_and(data[0] > 100, data[2] > 100)])

        if fit == 'linear':
            p0 = [1.0, 5.0]

            def fitfunc(p, x): return p[0]*x + p[1]
        elif fit == 'cubic':
            p0 = [.01, .01, 1.0, 0.0]

            def fitfunc(p, x): return p[0]*x**3 + p[1]*x**2 + p[2]*x + p[3]
        else:
            print("SA fitting function not defined!!!")

        def errfunc(p, x, y): return (fitfunc(p, x)-y)

        p, cov_p, info, mesg, ier \
            = leastsq(errfunc, p0, args=(sa_x, sa_y), full_output=1)

        if ier not in [1, 2, 3, 4] or cov_p is None:
            msg = "SA calibration optimal parameters not found: " + mesg
            raise RuntimeError(msg)
        if any(np.diag(cov_p) < 0):
            raise RuntimeError(
                "Optimal parameters not found: negative variance")

        chisq = np.dot(info["fvec"], info["fvec"])
        dof = len(info["fvec"]) - len(p)
        sigma = np.array([np.sqrt(cov_p[i, i])*np.sqrt(chisq/dof)
                          for i in range(len(p))])

        self.p = p
        self.sigma = sigma
        self.f = fitfunc
        
        self.data = (data[0][data[2] > 100], data[2][data[2] > 100])

    def sa_cm(self, x):
        return self.f(self.p, x)

    def get_data(self):
        return self.data