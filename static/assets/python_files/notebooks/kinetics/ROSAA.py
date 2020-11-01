
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
    print("\n##############################################\nLine shape")
    
    freq = conditions["freq"]  # transition frequency in Hz
    
    print(f"Transition frequency in Hz: {freq=:.2e}\n")
    
    # doppler line width
    massIon = conditions["IonMass(amu)"]
    tempIon = conditions["IonTemperature(K)"]
    sigma = gauss_fwhm(freq, massIon, tempIon)
    
    # power broadening
    dipoleMoment = conditions["dipoleMoment(D)"]
    power = conditions["power(W)"]
    
    cp = conditions["cp"]
    gamma = lorrentz_fwhm(dipoleMoment, power, cp)
    
    print(f"{sigma=:.2e}, {gamma=:.2e}")
    # normalised line shape factor
    LineShape = voigt(gamma, sigma)
    print(f"{LineShape=}")
    # transition rate due to influence of mm-wave 
    # normalisation factor
    
    trap_area = conditions["trap_area"]
    norm = (power/(trap_area*C))*LineShape
    print(f"Transition rate due to influence of mm-wave \nnormalisation factor: {norm:.2e}")
    ##############################################
    
    ##############################################
    # Einstein co-efficient
    ##############################################
    
    print("\n##############################################\nEinstein co-efficient")
    A_10 = conditions["SpontaneousEmission"]  
    B_10 = stimulated_emission(A_10, freq)
    B_01 = stimulated_absorption(0, 1, B_10)
    
    Rate_B_10 = B_10*norm
    Rate_B_01 = B_01*norm
    
    print(f"{Rate_B_01=:.2e}, {Rate_B_10=:.2e}")
    ##############################################
    
    ##############################################
    # Ternary attachment and collisional dissociation rates
    ##############################################
    print("\n##############################################\nTernary attachment and collisional dissociation rates")

    a = conditions["a"]
    k31_0, k32 = conditions["k3"]
    k31_1 = a*k31_0
    
    kCID1, kCID2 = conditions["kCID"]
    
    nHe = conditions["He density(cm3)"]
    
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
    print("\n##############################################\nCollisional rate")
    trapTemp = conditions["trapTemp(K)"]
    Energy = conditions["Energy"]
    
    q_10, q_20, q_21 = conditions["Collisional_q"]
    
    q_01 = q_10*distribution(1, 0, Energy[1], Energy[0], trapTemp)  # calculating q_up from q_down detailed balancing
    Rate_q_01 = q_01*nHe
    Rate_q_10 = q_10*nHe
    
    q_02 = q_20*distribution(2, 0, Energy[2], Energy[0], trapTemp)
    Rate_q_02 = q_02*nHe
    Rate_q_20 = q_20*nHe
    
    q_12 = q_21*distribution(2, 1, Energy[1], Energy[2], trapTemp)
    Rate_q_12 = q_12*nHe
    Rate_q_21 = q_21*nHe
    
    print(f"{Rate_q_01=:.2e}, {Rate_q_10=:.2e}\n{Rate_q_02=:.2e}, {Rate_q_20=:.2e}\n{Rate_q_12=:.2e}, {Rate_q_21=:.2e}")
    
    branching_ratio = conditions["branching-ratio"]
    
    ##############################################
    
    
    ##############################################
    # Boltzman distribution
    ##############################################
    
    numberOfLevel = conditions["numberOfLevel"]
    totalIonCounts = conditions["totalIonCounts"]
    
    boltzman_ratio = boltzman_distribution(Energy[:numberOfLevel], trapTemp)
    initialPopulation = boltzman_ratio*totalIonCounts
    
    ##############################################
    
    
    ##############################################
    # Signal(%) simulation
    ##############################################
    
    trapTime = conditions["trapTime(ms)"]/1000
    tspan = [0, trapTime]
    simulationTime = np.linspace(0, trapTime, 1000)
    
    print(f"{tspan=}")
    print(f"\nSolving for {initialPopulation=}")
    
    print("Kinetic simulation laser-OFF: Running")
    Noff = solve_ivp(kinetic_simulation_off, tspan, [*initialPopulation, 0, 0], t_eval=simulationTime)
    
    print("Kinetic simulation laser-ON: Running")
    Non = solve_ivp(kinetic_simulation_on, tspan, [*initialPopulation, 0, 0], t_eval=simulationTime)
    
    print("Simulation Done")
    ##############################################
    
    return Noff, Non



def main():

    t0 = perf_counter()
    conditions_HCO = {
        "power(W)": 1e-5,
        "branching-ratio":0.5,
        "trapTime(ms)":600, 
        "trapTemp(K)":5.7,
        "He density(cm3)":2.5e+14,
        "a":0.4,
        "IonTemperature(K)":15,
        "IonMass(amu)":29,
        "cp":1.5e8,
        "dipoleMoment(D)":None,
        "numberOfLevel":3,
        "totalIonCounts":1000,
        "trap_area":5.5e-5,
        "freq":89.2e9,
        "k3":[1.6e-30, 2.9e-30],
        "kCID":[3.5e-15, 9.0e-15],
        "Collisional_q":[10*2.2e-10, 10*0.857e-10, 10*1.152e-10],
        "SpontaneousEmission":4.187e-5,
        "Energy":[0, 2.975, 8.925, 17.8497, 29.7491, 44.6228, 62.4705, 83.2919] # in cm-1
    }

    conditions_CD = {
        "power(W)": 2e-5,
        "branching-ratio": 0.5,
        "trapTime(ms)": 600,
        "trapTemp(K)": 5,
        "He density(cm3)": 5e14,
        "a": 0.5,
        "IonTemperature(K)": 12.3,
        "IonMass(amu)": 14,
        "cp": 4.9e7,
        "dipoleMoment(D)": None,
        "numberOfLevel": 3,
        "totalIonCounts": 1000,
        "trap_area": 5e-5,
        "freq": 453_521_850_000,
        "k3": [9.6e-31, 2.9e-30],
        "kCID": [6.7e-16, 1.9e-15],
        "Collisional_q": [4.3242e-11, 3.4640e-11, 1.3013e-10],
        "SpontaneousEmission": 6.24e-4,
        "Energy": [0, 15.127861, 45.373851, 90.718526, 151.132755, 226.577764]
    }

    Noff, Non = ROSAA_modal(conditions_CD)

    t1 = perf_counter()
    print(f"Time taken: {(t1-t0)/60:.2f} minutes")
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
    main()