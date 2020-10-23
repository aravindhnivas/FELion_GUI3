
# Importing modules
import numpy as np
from scipy.constants import Boltzmann as k_boltzmann, speed_of_light as C,\
    Planck, m_p
from scipy.special import wofz


# Constants
epsilon = 8.854e-12
reduced_plank = Planck / (2*np.pi)
k_boltzmann_wavenumber = k_boltzmann/1.98630e-23

trap_area = 5e-5


def gauss_fwhm(freq, mass, temp):
    return freq * np.sqrt((8*k_boltzmann*temp*np.log(2)) / (m_p*mass*C**2))


def lorrentz_fwhm(dipole, power, cp=None):
    if cp > 0:
        return cp*np.sqrt(power)
    return (dipole*3.33564e-30)/(reduced_plank*np.pi*np.sqrt(C*epsilon*trap_area)) * np.sqrt(power)


def voigt(lorrentz, gaussian):
    faddava = 1j*lorrentz/(gaussian*np.sqrt(2))
    return (wofz(faddava) / (np.sqrt(2*np.pi) * gaussian)).real


def stimulated_emission(spontaneous_emission, freq):
    return (C**3 / (8*np.pi*Planck*freq**3)) * spontaneous_emission


def stimulated_absorption(j0, j1, emission): 
    return ((2*j1+1)/(2*j0+1)) * emission


def boltzman_distribution(energyLevels, temp=5):
    KT = k_boltzmann_wavenumber*temp
    Nj = [(2*i+1)*np.exp(-energy/KT) for i, energy in enumerate(energyLevels)]
    Nj = np.array(Nj, dtype=np.float)
    Nj = Nj/Nj.sum()
    return Nj


def distribution(j0, j1, energy, temp):
    KT = k_boltzmann_wavenumber*temp
    N0 = (2*j0+1)
    N1 = (2*j1+1)
    Gj = N1/N0

    delE = abs(energy[j0]-energy[j1])

    return Gj*np.exp(-delE/KT)


def showRateDistributionEquations(totallevel, excitedLevel, lightON, includeSpontaneousEmissionForAllLevels, nHe="nHe"):
    
    fullRateEquation = []
    N = [f"N{i}" for i in range(totallevel)]
    N_He = [f"{nHe}{i}" for i in range(2)]
    
    rateCollection = []
    
    if lightON:
        temp0 = f"B_{excitedLevel-1}{excitedLevel}"
        temp1 = f"B_{excitedLevel}{excitedLevel-1}"

        # defined B rate from excited state 
        B_rate = f" + {temp0}*{N[excitedLevel-1]} - {temp1}*{N[excitedLevel]} "
    
    # For loop for combining different rates processes
    for i in range(totallevel):
        
        # Collisional rate
        rateEquationsCombined = []
        for j in range(totallevel):
            if i!= j: 
                
                key = f"{j}{i}"
                keyInverse = f"{i}{j}"
                
                temp0 = f"q_{key}"
                temp1 = f"q_{keyInverse}"
                
                k0 = f" + {temp0}*{nHe}*{N[j]} - {temp1}*{nHe}*{N[i]}"
                
                rateEquationsCombined.append(k0)
        
        
        # END: Collisional rate for loop
        k1 = ""
        
        # Einstein Coefficient A
        if i == 0:
            temp0 = f"A_10"
            k1 += f" + {temp0}*{N[1]}"
        
        if includeSpontaneousEmissionForAllLevels:
            if i == totallevel-1:
                temp0 = f"A_{i}{i-1}"
                k1 += f" - {temp0}*{N[i]}"

            if i>0 and i<totallevel-1:
                temp0 = f"A_{i}{i-1}"
                temp1 = f"A_{i+1}{i}"
                k1 += f" - {temp0}*{N[i]} + {temp1}*{N[i+1]}"
                
        elif i == 1:
            temp0 = f"A_10"
            k1 += f" - {temp0}*{N[1]}"
            
        # END: Einstein Coefficient A
        
        
        # Einstein Coefficient B
        # NOTE: B rate defined from excited state
        
        if lightON:
            if i==excitedLevel-1:
                k1 += f" - ({B_rate})"

            if i==excitedLevel:
                k1 += f"{B_rate}"
        
        # END: Einstein Coefficient B

        # Combining all equations into single array
        rateEquationsCombined.append(k1)
        rateCollection.append(rateEquationsCombined)
        
    # END: For loop for combining different rates processes
    
    # Computing all rates
    dR_dt = []

    for rates in rateCollection:
        temp = reduce(lambda a, b: a+b, rates)
        dR_dt.append(temp)
        
    # Adding rare gas atom attachment and dissociation rates
    attachmentRate0 = f" - k31_0*{nHe}**2*{N[0]} + kCID1*{nHe}*{N_He[0]}*p"
    attachmentRate1 = f" - k31_1*{nHe}**2*{N[1]} + kCID1*{nHe}*{N_He[0]}*(1-p)"
    attachmentRate2 = f" - k32*{nHe}**2*{N_He[0]} + kCID2*{nHe}*{N_He[1]}"
    
    dR_dt[0] += attachmentRate0
    dR_dt[1] += attachmentRate1
    
    # CDHe:
    dCDHe_dt = attachmentRate0 + attachmentRate1 + attachmentRate2
    dR_dt.append(dCDHe_dt)
    
    # CDHe2
    dCDHe2_dt = f" - ({attachmentRate2})"
    dR_dt.append(dCDHe2_dt)
    
    for i, eq in enumerate(dR_dt):
        if i>=totallevel:
            fullRateEquation.append(f"NHe{i} = {eq}")
        else:
            fullRateEquation.append(f"N{i} = {eq}")
            
    return dR_dt, fullRateEquation