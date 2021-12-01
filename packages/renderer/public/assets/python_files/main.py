import sys
import json
import addTrace
import baseline
import collisionalSimulation
import delete_fileLines
import depletionscan
import exp_gauss_fit
import find_peaks_masspec
import fit_all
import getfile_details
import mass
import multiGauss
import normline
import oposcan
import theory
import thz_scan
import timescan
import collisionalFit
import voigt
import ROSAA_simulation
import kineticsCode
import weighted_error


functions = {
    "addTrace": addTrace,
    "baseline": baseline,
    "collisionalSimulation": collisionalSimulation,
    "delete_fileLines": delete_fileLines,
    "depletionscan": depletionscan,
    "exp_gauss_fit": exp_gauss_fit,
    "find_peaks_masspec": find_peaks_masspec,
    "fit_all": fit_all,
    "getfile_details": getfile_details,
    "mass": mass,
    "multiGauss": multiGauss,
    "normline": normline,
    "oposcan": oposcan,
    "theory": theory,
    "thz_scan": thz_scan,
    "timescan": timescan,
    "weighted_error": weighted_error,
    "kineticsCode": kineticsCode,
    "ROSAA_simulation": ROSAA_simulation,
    "voigt": voigt,
    "collisionalFit": collisionalFit,
}


if __name__ == "__main__":
    pyfile = sys.argv[1].split(".")[0]
    print(f"{pyfile=}", flush=True)

    args = json.loads(sys.argv[2])
    pyfuntion = functions[pyfile]
    pyfuntion.main(args)

