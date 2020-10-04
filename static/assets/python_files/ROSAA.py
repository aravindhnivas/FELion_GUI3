
import sys, json
import numpy as np
import matplotlib.pyplot as plt
# from pathlib import Path as pt
from scipy.integrate import solve_ivp
from numba import jit

from ROSAA_func import distribution, boltzman_distribution, \
    stimulated_absorption, stimulated_emission,\
    voigt, lorrentz_fwhm, gauss_fwhm
from time import perf_counter

from scipy.constants import speed_of_light as C

# Global variable

Rate_k31_0, Rate_k31_1, Rate_k32 = None, None, None

Rate_kCID1, Rate_kCID2 = None, None
Rate_q_01, Rate_q_02 = None, None
Rate_q_10, Rate_q_20 = None, None
Rate_q_12, Rate_q_21 = None, None
Rate_B_01, Rate_B_10 = None, None
A_10 = None

branching_ratio = None

@jit(nopython=True, fastmath=True)
def kinetic_simulation_off(t, N):

    CD0, CD1, CD2, CDHe, CDHe2 = N
    p = branching_ratio
    
    # CD: j=0
    attachmentRate0 = -Rate_k31_0*CD0 + Rate_kCID1*CDHe*p
    collisionalRate0 = -Rate_q_01*CD0 + Rate_q_10*CD1 + Rate_q_20*CD2 - Rate_q_02*CD0
    spontaneousEmissionRate = A_10*CD1

    dCD0_dt = attachmentRate0 + collisionalRate0 + spontaneousEmissionRate

    # CD: j=1
    attachmentRate1 = -Rate_k31_1*CD1 + Rate_kCID1*CDHe*(1-p)
    collisionalRate1 = Rate_q_01*CD0 - Rate_q_10*CD1 - Rate_q_12*CD1 + Rate_q_21*CD2

    dCD1_dt = attachmentRate1 + collisionalRate1 - spontaneousEmissionRate

    # CD: j=2
    collisionalRate2 = Rate_q_02*CD0 - Rate_q_20*CD2 + Rate_q_12*CD1 - Rate_q_21*CD2
    dCD2_dt = collisionalRate2

    # CDHe:
    attachmentRate2 = -Rate_k32*CDHe + Rate_kCID2*CDHe2
    dCDHe_dt = -attachmentRate0 - attachmentRate1 + attachmentRate2

    # CDHe2
    dCDHe2_dt = -attachmentRate2

    return [dCD0_dt, dCD1_dt, dCD2_dt, dCDHe_dt, dCDHe2_dt]


@jit(nopython=True, fastmath=True)
def kinetic_simulation_on(t, N):

    CD0, CD1, CD2, CDHe, CDHe2 = N
    p = branching_ratio
    # CD: j=0
    attachmentRate0 = -Rate_k31_0*CD0 + Rate_kCID1*CDHe*p
    collisionalRate0 = -Rate_q_01*CD0 + Rate_q_10*CD1 + Rate_q_20*CD2 - Rate_q_02*CD0
    spontaneousEmissionRate0 = A_10*CD1
    stimulatedRate = -Rate_B_01*CD0 + Rate_B_10*CD1

    dCD0_dt = attachmentRate0 + collisionalRate0 + spontaneousEmissionRate0 + stimulatedRate

    # CD: j=1
    attachmentRate1 = -Rate_k31_1*CD1 + Rate_kCID1*CDHe*(1-p)
    collisionalRate1 = Rate_q_01*CD0 - Rate_q_10*CD1 - Rate_q_12*CD1 + Rate_q_21*CD2
    spontaneousEmissionRate1 = -A_10*CD1

    dCD1_dt = attachmentRate1 + collisionalRate1 + spontaneousEmissionRate1 - stimulatedRate

    # CD: j=2
    collisionalRate2 = Rate_q_02*CD0 - Rate_q_20*CD2 + Rate_q_12*CD1 - Rate_q_21*CD2
    dCD2_dt = collisionalRate2

    # CDHe:
    attachmentRate2 = -Rate_k32*CDHe + Rate_kCID2*CDHe2
    dCDHe_dt = -attachmentRate0 - attachmentRate1 + attachmentRate2

    # CDHe2
    dCDHe2_dt = -attachmentRate2

    return [dCD0_dt, dCD1_dt, dCD2_dt, dCDHe_dt, dCDHe2_dt]


def ROSAA_modal(conditions):
    
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
    
    nHe = float(conditions["He density(cm3)"])
    
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
    
    q_01 = q_10*distribution(1, 0, Energy[1], Energy[0], trapTemp)  # calculating q_up from q_down detailed balancing
    Rate_q_01 = q_01*nHe
    Rate_q_10 = q_10*nHe
    
    q_02 = q_20*distribution(2, 0, Energy[2], Energy[0], trapTemp)
    Rate_q_02 = q_02*nHe
    Rate_q_20 = q_20*nHe
    
    q_12 = q_21*distribution(2, 1, Energy[1], Energy[2], trapTemp)
    Rate_q_12 = q_12*nHe
    Rate_q_21 = q_21*nHe
    
    print(f"{Rate_q_01=:.2e}, {Rate_q_10=:.2e}\n{Rate_q_02=:.2e}, {Rate_q_20=:.2e}\n{Rate_q_12=:.2e}, {Rate_q_21=:.2e}", flush=True)
    
    branching_ratio = float(conditions["branching-ratio"])
    
    ##############################################
    
    
    ##############################################
    # Boltzman distribution
    ##############################################
    
    numberOfLevel = int(conditions["numberOfLevel"])
    totalIonCounts = float(conditions["totalIonCounts"])
    
    boltzman_ratio = boltzman_distribution(Energy[:numberOfLevel], trapTemp)
    initialPopulation = boltzman_ratio*totalIonCounts
    
    ##############################################
    
    
    ##############################################
    # Signal(%) simulation
    ##############################################
    
    trapTime = float(conditions["trapTime(ms)"])/1000
    tspan = [0, trapTime]
    simulationTime = np.linspace(0, trapTime, 1000)
    
    print(f"{tspan=}")
    print(f"\nSolving for {initialPopulation=}", flush=True)
    
    t0 = perf_counter()

    print("Kinetic simulation laser-OFF: Running", flush=True)
    
    Noff = solve_ivp(kinetic_simulation_off, tspan, [*initialPopulation, 0, 0], t_eval=simulationTime)
    t1 = perf_counter()


    print(f"Time taken for OFF simulation: {(t1-t0)/60:.2f} minutes")
    print("Kinetic simulation laser-ON: Running", flush=True)
    
    
    
    Non = solve_ivp(kinetic_simulation_on, tspan, [*initialPopulation, 0, 0], t_eval=simulationTime)
    print("Simulation Done", flush=True)

    ##############################################
    
    return Noff, Non

def main(conditions):

    t0 = perf_counter()
    Noff, Non = ROSAA_modal(conditions)
    t1 = perf_counter()

    print(f"Time taken: {(t1-t0)/60:.2f} minutes", flush=True)
    mol = "CD"
    tag = "He"

    yoff = Noff.y.T
    yon = Non.y.T

    fig, ax = plt.subplots()

    lg = [f"{mol}(0)", f"{mol}(1)", f"{mol}(2)", f"{mol}{tag}", f"{mol}{tag}2"]
    c = 0
    for off, on in zip(Noff.y, Non.y):
        ax.plot(x, off, f"C{c}-", label=f"{lg[c]}")
        ax.plot(x, on, f"C{c}--")
        c += 1
        
    ax.set_yscale("log")
    ax.legend(title="- Off, -- On")
    plt.show()


if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    print(f"Received args: {args}, {type(args)}\n", flush=True)
    conditions = {}

    for i in args:
        i = list(i.items())
        conditions[f"{i[0][1]}"] = i[1][1]

    print(conditions, flush=True)
    main(conditions)