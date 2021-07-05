
import sys, json
from pathlib import Path as pt
import numpy as np
from scipy.special import voigt_profile
sys.path.insert(0, "D:/FELion_GUI3/static/assets/python_files")
from FELion_definitions import sendData

if __name__ == "__main__":
    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(args, flush=True)

    sigma = float(args["gaussian"])
    gamma = float(args["lorrentz"])
    dataToSend = {}
    
    linshape = float(voigt_profile(0, sigma, gamma))


    print(f"{sigma=}\n{gamma=}\n{linshape=}", flush=True)
    print(f"{sigma=}\n{gamma=}\n{linshape=}", flush=True)
    print(f"{voigt_profile(0, 0, 1)=}", flush=True)
    dataToSend["linshape"] = linshape
    sendData(dataToSend)