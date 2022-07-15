from pathlib import Path as pt
import numpy as np
from scipy.special import voigt_profile
from felionlib.utils.FELion_definitions import sendData


def main(args, saveData=True):
    fG = float(args["gaussian"]) * 1e6  # MHz --> Hz
    fL = float(args["lorrentz"]) * 1e6
    sigma = fG / (2 * np.sqrt(2 * np.log(2)))
    gamma = fL / 2
    lineShape = float(voigt_profile(0, sigma, gamma))
    dataToSend = {"lineShape": lineShape}

    if saveData:
        sendData(dataToSend, calling_file=pt(__file__).stem)
    return lineShape
