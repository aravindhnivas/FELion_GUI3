
import sys, json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path as pt
from scipy.integrate import solve_ivp
# from numba import jit

from ROSAA_func import distribution, boltzman_distribution, \
    stimulated_absorption, stimulated_emission,\
    voigt, lorrentz_fwhm, gauss_fwhm
from time import perf_counter

from scipy.constants import speed_of_light as C

from concurrent.futures import ProcessPoolExecutor

# Global variable

Rate_k31_0, Rate_k31_1, Rate_k32 = None, None, None

Rate_kCID1, Rate_kCID2 = None, None
Rate_q_01, Rate_q_02 = None, None
Rate_q_10, Rate_q_20 = None, None
Rate_q_12, Rate_q_21 = None, None
Rate_B_01, Rate_B_10 = None, None
A_10 = None

branching_ratio = None

# @jit(nopython=True, fastmath=True, nogil=True)
def kinetic_simulation_off(t, N):

    CD0, CD1, CD2, CDHe, CDHe2 = N
    p = branching_ratio
    
    # CD: j=0
    attachmentRate0 = -Rate_k31_0*CD0 + Rate_kCID1*CDHe*p
    collisionalRate0 = (-Rate_q_01*CD0 + Rate_q_10*CD1 + Rate_q_20*CD2 - Rate_q_02*CD0) if includeCollision else 0
    spontaneousEmissionRate = A_10*CD1

    dCD0_dt = attachmentRate0 + collisionalRate0 + spontaneousEmissionRate

    # CD: j=1
    attachmentRate1 = -Rate_k31_1*CD1 + Rate_kCID1*CDHe*(1-p)
    collisionalRate1 = (Rate_q_01*CD0 - Rate_q_10*CD1 - Rate_q_12*CD1 + Rate_q_21*CD2) if includeCollision else 0

    dCD1_dt = attachmentRate1 + collisionalRate1 - spontaneousEmissionRate

    # CD: j=2
    collisionalRate2 = (Rate_q_02*CD0 - Rate_q_20*CD2 + Rate_q_12*CD1 - Rate_q_21*CD2) if includeCollision else CD2
    dCD2_dt = collisionalRate2

    # CDHe:
    attachmentRate2 = -Rate_k32*CDHe + Rate_kCID2*CDHe2
    dCDHe_dt = -attachmentRate0 - attachmentRate1 + attachmentRate2

    # CDHe2
    dCDHe2_dt = -attachmentRate2

    return [dCD0_dt, dCD1_dt, dCD2_dt, dCDHe_dt, dCDHe2_dt]


def kinetic_simulation_on(t, N):

    CD0, CD1, CD2, CDHe, CDHe2 = N

    p = branching_ratio

    # CD: j=0
    attachmentRate0 = -Rate_k31_0*CD0 + Rate_kCID1*CDHe*p
    collisionalRate0 = (-Rate_q_01*CD0 + Rate_q_10*CD1 + Rate_q_20*CD2 - Rate_q_02*CD0) if includeCollision else 0
    spontaneousEmissionRate = A_10*CD1
    stimulatedRate = -Rate_B_01*CD0 + Rate_B_10*CD1


    dCD0_dt = attachmentRate0 + collisionalRate0 + spontaneousEmissionRate + stimulatedRate

    # CD: j=1
    attachmentRate1 = -Rate_k31_1*CD1 + Rate_kCID1*CDHe*(1-p)
    collisionalRate1 = (Rate_q_01*CD0 - Rate_q_10*CD1 - Rate_q_12*CD1 + Rate_q_21*CD2) if includeCollision else 0

    dCD1_dt = attachmentRate1 + collisionalRate1 - spontaneousEmissionRate - stimulatedRate

    # CD: j=2
    collisionalRate2 = (Rate_q_02*CD0 - Rate_q_20*CD2 + Rate_q_12*CD1 - Rate_q_21*CD2) if includeCollision else CD2
    dCD2_dt = collisionalRate2

    # CDHe:
    attachmentRate2 = -Rate_k32*CDHe + Rate_kCID2*CDHe2
    dCDHe_dt = -attachmentRate0 - attachmentRate1 + attachmentRate2
    # CDHe2
    dCDHe2_dt = -attachmentRate2

    return [dCD0_dt, dCD1_dt, dCD2_dt, dCDHe_dt, dCDHe2_dt]


def ROSAA_modal(args):
    conditions, nHe = args
    
    global Rate_k31_0, Rate_k31_1, Rate_k32, \
            Rate_kCID1, Rate_kCID2,\
            Rate_q_01, Rate_q_02,\
            Rate_q_10, Rate_q_20,\
            Rate_q_12, Rate_q_21,\
            Rate_B_01, Rate_B_10,\
            A_10, branching_ratio
    
    ##############################################
    # Line shape
    ##############################################
    print("\n##############################################\nLine shape", flush=True)
    
    freq = float(conditions["freq"])  # transition frequency in Hz
    print(f"Transition frequency in Hz: {freq=:.2e}\n", flush=True)
    
    # doppler line width

    massIon = float(conditions["IonMass(amu)"])
    tempIon = float(conditions["IonTemperature(K)"])
    sigma = gauss_fwhm(freq, massIon, tempIon)
    
    # power broadening
    dipoleMoment = float(conditions["dipoleMoment(D)"])
    power = float(conditions["power(W)"])
    
    cp = float(conditions["cp"])
    gamma = lorrentz_fwhm(dipoleMoment, power, cp)
    
    print(f"{sigma=:.2e}, {gamma=:.2e}")
    # normalised line shape factor
    LineShape = voigt(gamma, sigma)
    print(f"{LineShape=}")
    # transition rate due to influence of mm-wave 
    # normalisation factor
    
    trap_area = float(conditions["trap_area"])
    norm = (power/(trap_area*C))*LineShape
    print(f"Transition rate due to influence of mm-wave \nnormalisation factor: {norm:.2e}", flush=True)
    ##############################################
    
    ##############################################
    # Einstein co-efficient
    ##############################################
    
    print("\n##############################################\nEinstein co-efficient", flush=True)
    A_10 = float(conditions["SpontaneousEmission"]  )
    B_10 = stimulated_emission(A_10, freq)
    B_01 = stimulated_absorption(0, 1, B_10)
    
    Rate_B_10 = B_10*norm
    Rate_B_01 = B_01*norm
    
    print(f"{Rate_B_01=:.2e}, {Rate_B_10=:.2e}")
    ##############################################
    
    ##############################################
    # Ternary attachment and collisional dissociation rates
    ##############################################

    print("\n##############################################\nTernary attachment and collisional dissociation rates", flush=True)
    
    a = float(conditions["a"])
    k31_0, k32 = [float(i.strip()) for i in conditions["k3"].split(",")]
    k31_1 = a*k31_0
    
    kCID1, kCID2 = [float(i.strip()) for i in conditions["kCID"].split(",")]
    
    
    Rate_k31_0 = k31_0*nHe**2
    Rate_k31_1 = k31_1*nHe**2
    Rate_k32 = k32*nHe**2
    Rate_kCID1 = kCID1*nHe
    Rate_kCID2 = kCID2*nHe
    
    print(f"{Rate_k31_0=:.2e}, {Rate_k31_1=:.2e}, {Rate_k32=:.2e}")
    print(f"{Rate_kCID1=:.2e}, {Rate_kCID2=:.2e}")
    
    ##############################################
    
    ##############################################
    # Collisional rate
    
    ##############################################
    print("\n##############################################\nCollisional rate", flush=True)
    trapTemp = float(conditions["trapTemp(K)"])
    Energy = [float(i.strip()) for i in conditions["Energy"].split(",")]
    
    q_10, q_20, q_21 = [float(i.strip()) for i in conditions["Collisional_q"].split(",")]
    
    # KT = 0.695035*trapTemp
    # g = [1, 3, 5, 7, 9, 11]

    q_01 = q_10 * distribution(0, 1, Energy, trapTemp)   # calculating q_up from q_down detailed balancing
    Rate_q_01 = q_01*nHe
    Rate_q_10 = q_10*nHe
    
    q_02 = q_20*distribution(0, 2, Energy, trapTemp)
    Rate_q_02 = q_02*nHe
    Rate_q_20 = q_20*nHe
    
    q_12 = q_21*distribution(1, 2, Energy, trapTemp)
    Rate_q_12 = q_12*nHe
    Rate_q_21 = q_21*nHe
    
    print(f"{Rate_q_01=:.2e}, {Rate_q_10=:.2e}\n{Rate_q_02=:.2e}, {Rate_q_20=:.2e}\n{Rate_q_12=:.2e}, {Rate_q_21=:.2e}", flush=True)
    
    branching_ratio = float(conditions["branching-ratio"])
    
    ##############################################
    
    
    ##############################################
    # Boltzman distribution
    ##############################################
    numberOfLevel = int(conditions["numberOfLevel (J levels)"])

    totalIonCounts = float(conditions["totalIonCounts"])
    
    boltzman_ratio = boltzman_distribution(Energy[:numberOfLevel], trapTemp)
    initialPopulation = boltzman_ratio*totalIonCounts
    
    ##############################################
    
    
    ##############################################
    # Signal(%) simulation
    ##############################################
    
    trapTime = float(conditions["Simulation time(ms)"])/1000
    tspan = [0, trapTime]
    Nsteps = int(conditions["Total steps"])

    simulationTime = np.linspace(0, trapTime, Nsteps)
    
    print(f"{tspan=}")
    print(f"\nSolving for {initialPopulation=}", flush=True)
    
    t0 = perf_counter()
    print("Kinetic simulation laser-OFF: Running", flush=True)
    
    Noff = solve_ivp(kinetic_simulation_off, tspan, [*initialPopulation, 0, 0], t_eval=simulationTime)
    t1 = perf_counter()

    print(f"Time taken for OFF simulation: {(t1-t0)/60:.2f} minutes")

    
    
    print("Kinetic simulation laser-ON: Running", flush=True)
    

    Non = solve_ivp(kinetic_simulation_on, tspan, [*initialPopulation, 0, 0], t_eval=simulationTime)
    
    ##############################################
    
    _on = np.array(Non.y[numberOfLevel], dtype=float)
    _off = np.array(Noff.y[numberOfLevel], dtype=float)

    signal = 1 - (_on[-1] / _off[-1])
    
    print(f"Signal(%) = {signal*100:.2f}")
    
    return Noff, Non


def writeFile(counts, filename=None, label="off"):

    # if filename == None: filename = conditions["filename"]
    with open(location/f"{filename}_{label}.txt", "w+") as f:
        f.write("###################### Simulation begins ######################\n")
        
        f.write(f"# {mol}(0)\t{mol}(1)\t{mol}(2)\t{mol}{tag}\t{mol}{tag}2\n")

        for _count in counts:
            for _ in _count: 
                f.write(f"{_:.2f}\t")
            f.write("\n")
        
        f.write("###################### Simulation Done ######################")


def main(conditions):

    nHe = float(conditions["He density(cm3)"])

    write = bool(conditions["writefile"])

    t0 = perf_counter()
    variable = conditions["variable"]

    Noff_nHe = []
    Non_nHe = []
    signal_nHe = []
    
    if variable == "He density(cm3)":
    
        _min, _max, _step = [float(i) for i in conditions["range"].split(",")]
        _range = np.linspace(int(_min), int(_max), int(_step))
    
        print("Simulation wrt He/Ne number density")

        parameters = [(conditions, nHe) for nHe in _range]
        with ProcessPoolExecutor() as executor:
            results = executor.map(ROSAA_modal, parameters)
        
        for i, N in enumerate(results):
            Noff, Non = N
            Noff_nHe.append(Noff.y)
            Non_nHe.append(Non.y)
            _signal = 1 - (Non.y[numberOfLevel][-1] / Noff.y[numberOfLevel][-1])
            signal_nHe.append(_signal)



            if write:
                writeFile(Noff.y.T, label=f"{_range[i]:.2e}_off")
                writeFile(Non.y.T, label=f"{_range[i]:.2e}_on")

        
        signal_nHe = np.array(signal_nHe, dtype=float)*100
        Noff_nHe = np.array(Noff_nHe, dtype=float)
        Non_nHe = np.array(Non_nHe, dtype=float)
        
        if write:

            with open(location/f"{filename}_{int(_min):.2e}_{int(_max):.2e}_nHe.txt", "w+") as f:
                f.write("# Number density(cm3)\tSignal(%)\n")
            
                for _nd, _signal_nHe in zip(_range, signal_nHe):
                    f.write(f"{_nd:.2e}\t{_signal_nHe}\n")
        print(signal_nHe)

    else:
        Noff, Non = ROSAA_modal((conditions, nHe))
        
        if write:

            print(f"Writing into file\n")
            writeFile(Noff.y.T, label="off")
            writeFile(Non.y.T, label="on")

    t1 = perf_counter()
    print("Simulation Done", flush=True)
    print(f"Time taken: {(t1-t0)/60:.2f} minutes", flush=True)

    
    fig, (ax, ax1) = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
    lg = [f"{mol}(0)", f"{mol}(1)", f"{mol}(2)", f"{mol}{tag}", f"{mol}{tag}2"]


    c = 0
    time = Noff.t
    for off, on in zip(Noff.y, Non.y):
        ax.plot(time, off, f"C{c}-", label=f"{lg[c]}")
        ax.plot(time, on, f"C{c}--")
        c += 1

    ax.plot(time, Noff.y.sum(axis=0), f"k-", label="SUM")
    ax.plot(time, Non.y.sum(axis=0), f"k--")


    if variable == "He density(cm3)":
        lg = f"Max. Signal = {signal_nHe.max():.2f} at {(_range[signal_nHe.argmax()]):.2e}cm3"
        ax1.plot(_range, signal_nHe, label=lg)


        ax1.set(xlabel="He density(cm3)", ylabel=f"Signal (%) ({mol}{tag})", title="Signal(time)")
    else:


        _off = Noff.y[numberOfLevel][1:]
        _on = Non.y[numberOfLevel][1:]
        ratio = _on/_off
        
        signal = (1 - ratio)*100

        ax1.plot(time[1:], signal)
        ax1.set(xlabel="Time (s)", ylabel=f"Signal (%) ({mol}{tag})", title="Signal(time)")

        ax1.legend([f"Max. Signal = {signal.max():.2f} at {(time[1:][signal.argmax()]*1e3):.2f}ms"])

    ax.set_yscale("log")
    ax.set(xlabel="Time (s)", ylabel="Counts", title="Simulation")
    
    ax.legend(title="-- On, - Off")
    
    fig.savefig(location/f"{filename}.pdf", dpi=200)
    fig.savefig(location/f"{filename}.png", dpi=200)

    plt.tight_layout()
    plt.show()

includeCollision = None

if __name__ == "__main__":
    # global includeCollision
    args = sys.argv[1:][0].split(",")

    args = json.loads(", ".join(args))
    print(f"{args=}")
    # conditions = {}

    # for i in args:
    #     i = list(i.items())
    #     conditions[f"{i[0][1]}"] = i[1][1]

    # location = pt(conditions["currentLocation"])

    # filename = conditions["filename"]
    # mol = conditions["molecule"]
    # tag = conditions["tagging partner"]

    # numberOfLevel = int(conditions["numberOfLevel (J levels)"])
    # print(f"{location=}, {filename=}", flush=True)

    # includeCollision = bool(conditions["includeCollision"])

    # main(conditions)