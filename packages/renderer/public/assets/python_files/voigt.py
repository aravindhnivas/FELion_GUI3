
import sys, json
from pathlib import Path as pt
import numpy as np
from scipy.special import voigt_profile
main_module_loc = str(pt(__file__).joinpath("../../"))
sys.path.insert(0, main_module_loc)

from FELion_definitions import sendData

# args = None
def main(args):

    # global args
    # args = arguments
    # args = json.loads(sys.argv[1])

    print(args, flush=True)

    fG = float(args["gaussian"])*1e6
    
    fL = float(args["lorrentz"])*1e6


    sigma = fG/(2*np.sqrt(2*np.log(2)))
    gamma = fL/2
    linshape = float(voigt_profile(0, sigma, gamma))
    dataToSend = {"linshape" : linshape}
    sendData(dataToSend, calling_file=pt(__file__).stem)