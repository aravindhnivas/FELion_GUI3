
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
