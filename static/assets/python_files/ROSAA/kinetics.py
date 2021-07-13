
import sys, json, pprint
# from pathlib import Path as pt
import numpy as np
# from scipy.optimize import curve_fit
# main_module_loc = str(pt(__file__).joinpath("../../"))
# sys.path.insert(0, main_module_loc)

# from FELion_definitions import sendData
# from timescan import timescanplot

def KineticMain(args):

    scanfile = args["scanfile"]
    # data = timescanplot(scanfile)
    # time, mean, error, mass, t_res, t_b0 = data.get_data()




if __name__ == "__main__":
    # raise Exception("Error")
    args = json.loads(sys.argv[1])
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(args)
    sys.stdout.flush()

    # KineticMain(args)