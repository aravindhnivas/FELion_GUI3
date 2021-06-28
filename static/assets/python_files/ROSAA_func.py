
# Importing modules
import numpy as np
from scipy.constants import Boltzmann as k_boltzmann, speed_of_light as C,\
    Planck, m_p
from scipy.special import wofz


# Constants
epsilon = 8.854e-12
reduced_plank = Planck / (2*np.pi)
k_boltzmann_wavenumber = k_boltzmann/1.98630e-23

# trap_area = 5e-5

def gauss_fwhm(freq, mass, temp):

    return freq * np.sqrt((8*k_boltzmann*temp*np.log(2)) / (m_p*mass*C**2))


def lorrentz_fwhm(dipole, power, cp, trap_area):
    if cp > 0:
        return cp*np.sqrt(power)
    return (dipole*3.33564e-30)/(reduced_plank*np.pi*np.sqrt(C*epsilon*trap_area)) * np.sqrt(power)


def voigt(lorrentz, gaussian):
    faddava = 1j*lorrentz/(gaussian*np.sqrt(2))
    return (wofz(faddava) / (np.sqrt(2*np.pi) * gaussian)).real


def stimulated_emission(spontaneous_emission, freq):
    return (C**3 / (8*np.pi*Planck*freq**3)) * spontaneous_emission


def stimulated_absorption(j0, j1, emission, electronSpin=False, zeemanSplit=False):

    if electronSpin:
        if zeemanSplit:
            Gj = 1
        else:
            ground = float(j0.split("_")[1])
            excited = float(j1.split("_")[1])
            N0 = int(2*ground+1)
            N1 = int(2*excited+1)

            Gj = N1/N0
            
        
    else:

        if zeemanSplit:
            Gj = 1
        else:
            ground = int(j0)
            excited = int(j1)
            N0 = int(2*ground+1)
            N1 = int(2*excited+1)

            Gj = N1/N0
    return Gj * emission

def boltzman_distribution(energy_levels, temp=5, electronSpin=False, zeemanSplit=False):
    
    KT = k_boltzmann_wavenumber*temp
    Nj = []

    for label, energy in energy_levels.items():

        if electronSpin:
            if zeemanSplit:
                Gj = 1
            else:
                j = float(label.split("_")[1])
                Gj = int(2*j+1)
                
        else:
            if zeemanSplit:
                Gj = 1
            else:
                j = int(label)
                Gj = int(2*j+1)
        temp = Gj*np.exp(-energy/KT)
        Nj.append(temp)

    Nj = np.array(Nj, dtype=np.float)
    Nj = Nj/Nj.sum()
    return Nj

def distribution(j0, j1, energy_levels, temp, electronSpin, zeemanSplit):

    # defined for excitation rate constants
    KT = k_boltzmann_wavenumber*temp

    if electronSpin:
        if zeemanSplit:
            Gj = 1
        else:
            ground = float(j0.split("_")[1])
            excited = float(j1.split("_")[1])
            N0 = int(2*ground+1)
            N1 = int(2*excited+1)

            Gj = N1/N0
    else:
        if zeemanSplit:
            Gj = 1
        else:
            ground = int(j0)
            excited = int(j1)
            N0 = int(2*ground+1)
            N1 = int(2*excited+1)

            Gj = N1/N0
    
    delE = abs(energy_levels[f"{j0}"]-energy_levels[f"{j1}"])
    return Gj*np.exp(-delE/KT)