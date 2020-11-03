
from scipy.constants import Boltzmann, Planck, speed_of_light
import numpy as np

k_boltzmann_wavenumber = Boltzmann/1.98630e-23
def boltzman_distribution(energyLevels, temp=5):
    KT = k_boltzmann_wavenumber*temp
    Nj = [(2*i+1)*np.exp(-energy/KT) for i, energy in enumerate(energyLevels)]
    Nj = np.array(Nj, dtype=np.float)
    Nj = Nj/Nj.sum()
    return Nj


def mhz_wavenumber(freq):
    return freq*1e6/(speed_of_light*100)
mhz_wn = np.vectorize(mhz_wavenumber)