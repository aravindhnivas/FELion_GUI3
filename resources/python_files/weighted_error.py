# Importing Modules
import sys

# Data analysis
import numpy as np
from uncertainties import ufloat as uf, unumpy as unp
from FELion_definitions import sendData

def calc_error(data):

    x, s = data
    p =1/s**2

    sum_p = np.sum(p)
    # weighted_mean = np.sum(x*p)/sum_p
    weighted_mean = np.average(x, weights=p)

    s_int = 1 / np.sqrt(sum_p)

    N = len(x)

    # weighted_varience = np.sum(p*(x-weighted_mean)**2)/sum_p
    weighted_varience =  np.average((x-weighted_mean)**2, weights=p)
    s_ext = np.sqrt(weighted_varience/(N-1))
    
    u_arithmetic_mean = unp.uarray(x, s).mean()
    u_weighted_mean = uf(weighted_mean, max(s_int, s_ext))

    dataToSend = {"S_int":s_int, "S_ext":s_ext, "weighted_mean":weighted_mean, "weighted_s": max(s_int, s_ext), 
        "unweighted_mean":np.mean(x), "unweigted_s":np.std(x), "mean":f"{u_arithmetic_mean:.2uP}", "wmean":f"{u_weighted_mean:.2uP}"}
    return dataToSend

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")

    print(f"Received args: {args}")

    if len(args[0]) > 0:
        data = [float(i) for i in args]
        
        freq = data[0::8]
        amp = data[2::8]
        fwhm = data[4::8]
        sigma = data[6::8]

        freq_err = data[1::8]
        amp_err = data[3::8]
        fwhm_err = data[5::8]
        sigma_err = data[7::8]

        value = np.array([freq, amp, fwhm, sigma], dtype=float)
        err = np.array([freq_err, amp_err, fwhm_err, sigma_err], dtype=float)
        print(f"Converted data:\n {value} \n{err}")
        receiveData = []
        for x, y in zip(value, err):
            receiveData.append(calc_error([x, y]))

        dataToSend = {"freq":receiveData[0], "amp":receiveData[1], "fwhm":receiveData[2], "sig":receiveData[3]}
        sendData(dataToSend, calling_file=pt(__file__).stem)
    else: print("No lines available")