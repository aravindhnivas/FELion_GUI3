# Importing Modules
import sys

# Data analysis
import numpy as np
from uncertainties import ufloat as uf
from FELion_definitions import sendData

def calc_error(data):

    x, s = np.array(data, dtype=np.float)
    p =1/s**2

    sum_p = np.sum(p)
    weighted_mean = np.sum(x*p)/sum_p
    s_int = 1 / np.sqrt(sum_p)

    N = len(x)

    weighted_varience = np.sum(p*(x-weighted_mean)**2)/sum_p
    s_ext = np.sqrt(weighted_varience/(N-1))
    u_arithmetic_mean = uf(np.mean(x), np.std(x))
    u_weighted_mean = uf(weighted_mean, max(s_int, s_ext))
    dataToSend = {"S_int":s_int, "S_ext":s_ext, "weighted_mean":weighted_mean, "weighted_s": max(s_int, s_ext), 
        "unweighted_mean":np.mean(x), "unweigted_s":np.std(x), "mean":f"{u_arithmetic_mean:.2uP}", "wmean":f"{u_weighted_mean:.2uP}"}

    sendData(dataToSend)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    print(f"Received args: {args}")

    if len(args[0]) > 0:

        data = [float(i) for i in args]
        print(f"Converted data: {data}")
        
        line = data[::2]
        print(f"Error: {line}")

        err = data[1::2]
        print(f"Error: {err}")

        calc_error(data=[line, err])

    else: print("No lines available")