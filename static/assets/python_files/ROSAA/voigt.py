
import sys, json
from pathlib import Path as pt
import numpy as np
from scipy.special import voigt_profile
main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)

from FELion_definitions import sendData

if __name__ == "__main__":


    args = sys.argv[1:][0].split(",")

    args = json.loads(", ".join(args))

    print(args, flush=True)


    fG = float(args["gaussian"])*1e6
    fL = float(args["lorrentz"])*1e6
    dataToSend = {}

    sigma = fG/(2*np.sqrt(2*np.log(2)))
    gamma = fL/2
    linshape = float(voigt_profile(0, sigma, gamma))

    print(f"{sigma=}\n{gamma=}\n{linshape=}", flush=True)
    print(f"{sigma=}\n{gamma=}\n{linshape=}", flush=True)
    print(f"{voigt_profile(0, 0, 1)=}", flush=True)
    dataToSend["linshape"] = linshape
    sendData(dataToSend)