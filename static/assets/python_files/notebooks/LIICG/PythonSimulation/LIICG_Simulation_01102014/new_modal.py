
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from scipy.constants import Boltzmann as k_boltzmann, speed_of_light as C, Planck, m_p
from scipy.special import wofz

epsilon = 8.854e-12
reduced_plank = Planck / (2*np.pi)

k_boltzmann_wavenumber = k_boltzmann/1.98630e-23
trap_area=5.5e-5


def gauss_fwhm(freq, mass, temp): return freq * np.sqrt( (8*k_boltzmann*temp*np.log(2)) / (m_p*mass*C**2))
def lorrentz_fwhm(dipole, power): return ( dipole*3.33564e-30 ) /( reduced_plank*np.pi*np.sqrt(C*epsilon*trap_area) ) * np.sqrt(power)

def faddava_func(lorrentz, gaussian): return 1j*lorrentz/(gaussian*np.sqrt(2))
def voigt(lorrentz, gaussian): return (wofz(faddava_func(lorrentz, gaussian)) / (np.sqrt(2*np.pi) * gaussian)).real

def stimulated_emission(spontaneous_emission, freq): return ( C**3 / (8*np.pi*Planck*freq**3) ) * spontaneous_emission
def stimulated_absorption(j0, j1, emission): return ((2*j1+1)/(2*j0+1)) * emission

def boltzman_distribution(energyLevels, temp=5):
    KT = k_boltzmann_wavenumber*temp
    Nj = [(2*i+1)*np.exp(-energy/KT) for i, energy in enumerate(energyLevels)]
    Nj = np.array(Nj, dtype=np.float)
    Nj = Nj/Nj.sum()
    return Nj

def distribution(j0, j1, e0, e1, temp):
    KT = k_boltzmann_wavenumber*temp
    N0 = (2*j0+1)*np.exp(-e0/KT)
    N1 = (2*j1+1)*np.exp(-e1/KT)
    return N0/N1



def ROSAA_modal(conditions):
    
    ##############################################
    # Line shape
    ##############################################
    
    freq = conditions["freq"]  # transition frequency in Hz
    
    # doppler line width
    massIon = conditions["IonMass(amu)"]
    tempIon = conditions["IonTemperature(K)"]
    sigma = gauss_fwhm(freq, massIon, tempIon)
    
    # power broadening
    dipoleMoment = conditions["dipoleMoment(D)"]
    power = conditions["power(W)"]
    gamma = lorrentz_fwhm(dipoleMoment, power)
    
    # normalised line shape factor
    LineShape = voigt(gamma, sigma)
    
    # transition rate due to influence of mm-wave 
    # normalisation factor
    
    trap_area = conditions["trap_area"]
    norm = (power/(trap_area*C))*LineShape
    
    ##############################################
    
    ##############################################
    # Einstein co-efficient
    ##############################################
    
    A_10 = conditions["SpontaneousEmission"]  
    B_10 = stimulated_emission(A_10, freq)
    B_01 = stimulated_absorption(0, 1, B_10)
    
    Rate_B_10 = B_10*norm
    Rate_B_01 = B_01*norm
    
    ##############################################
    
    ##############################################
    # Ternary attachment and collisional dissociation rates
    ##############################################
    
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
    ##############################################
    
    ##############################################
    # Collisional cooling rate
    ##############################################
    
    trapTemp = conditions["trapTemp(K)"]
    Energy = conditions["Energy"]
    
    q_01, q_02, q_12 = conditions["Collisional_q"]
    
    q_10 = q_01*distribution(0, 1, Energy[0], Energy[1], trapTemp)  # calculating q_up from q_down detailed balancing
    Rate_q_01 = q_01*nHe
    Rate_q_10 = q_10*nHe
    
    q_20 = q_02*distribution(0, 2, Energy[0], Energy[2], trapTemp)
    Rate_q_02 = q_02*nHe
    Rate_q_20 = q_20*nHe
    
    q_21 = q_12*distribution(1, 2, Energy[1], Energy[2], trapTemp)
    Rate_q_12 = q_12*nHe
    Rate_q_21 = q_21*nHe
    
    ##############################################
    
    ##############################################
    # Simulation rates
    ##############################################
    
    p = conditions["branching-ratio"]
    
    def kinetic_simulation_off(t, N):
        
        CD0, CD1, CD2, CDHe, CDHe2 = N
        
        # CD: j=0
        attachmentRate0 = -Rate_k31_0*CD0 + Rate_kCID1*CDHe*p
        collisionalRate0 = -Rate_q_01*CD0 + Rate_q_10*CD1 + Rate_q_20*CD2 - Rate_q_02*CD0
        spontaneousEmissionRate0 = A_10*CD0
        
        dCD0_dt = attachmentRate0 + collisionalRate0 + spontaneousEmissionRate0
        
        # CD: j=1
        attachmentRate1 = -Rate_k31_1*CD1 + Rate_kCID1*CDHe*(1-p)
        collisionalRate1 = Rate_q_01*CD0 - Rate_q_10*CD1 - Rate_q_12*CD1 + Rate_q_21*CD2
        spontaneousEmissionRate1 = -A_10*CD1
        
        dCD1_dt = attachmentRate1 + collisionalRate1 + spontaneousEmissionRate1
        
        # CD: j=2
        collisionalRate2 = Rate_q_02*CD0 - Rate_q_20*CD2 + Rate_q_12*CD1 - Rate_q_21*CD2
        dCD2_dt = collisionalRate2
        
        # CDHe:
        attachmentRate2 = -Rate_k32*CDHe + Rate_kCID2*CDHe2
        dCDHe_dt = -attachmentRate0 - attachmentRate1 + attachmentRate2
        
        # CDHe2
        dCDHe2_dt = -attachmentRate2
        
        return [dCD0_dt, dCD1_dt, dCD2_dt, dCDHe_dt, dCDHe2_dt]
    
    def kinetic_simulation_on(t, N):
        
        CD0, CD1, CD2, CDHe, CDHe2 = N

        # CD: j=0
        attachmentRate0 = -Rate_k31_0*CD0 + Rate_kCID1*CDHe*p
        collisionalRate0 = -Rate_q_01*CD0 + Rate_q_10*CD1 + Rate_q_20*CD2 - Rate_q_02*CD0
        spontaneousEmissionRate0 = A_10*CD0
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
    
    
    Noff = solve_ivp(kinetic_simulation_off, tspan, [*initialPopulation, 0, 0], dense_output=True)
    Non = solve_ivp(kinetic_simulation_on, tspan, [*initialPopulation, 0, 0], dense_output=True)
    
    ##############################################
    
    return Noff, Non

conditions = {
    "power(W)": 2e-5,
    "branching-ratio":0.5,
    "trapTime(ms)":600, 
    "trapTemp(K)":5.7,
    "He density(cm3)":5e14,
    "a":0.5,
    "IonTemperature(K)":12.3,
    "IonMass(amu)":14,
    "dipoleMoment(D)":1.313,
    "numberOfLevel":3,
    "totalIonCounts":1000,
    "trap_area":5.5e-5,
    "freq":453_521_850_000,
    "k3":[9.6e-31, 2.9e-30],
    "kCID":[6.7e-16, 1.9e-15],
    "Collisional_q":[1*4.3242e-11, 1*3.4640e-11, 1*1.3013e-10],
    "SpontaneousEmission":6.24e-4,
    "Energy":[0, 15.127861, 45.373851, 90.718526, 151.132755, 226.577764]
}

Noff, Non = ROSAA_modal(conditions)

print(Noff, Non)