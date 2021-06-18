from numpy.core.multiarray import dtype

__author__ = 'kluge_admin'

import numpy as np
import matplotlib.pyplot as plt
from scipy import special
from Class_Definitions import Ions
from Class_Definitions import Conditions
from Class_Definitions import Ratecoefficients
from Class_Definitions import Time
from Class_Definitions import Fonts
from Class_Definitions import Rates

F = Fonts()
I = Ions()
CD = Conditions()
R = Ratecoefficients()
F = Fonts()
T = Time()
RA = Rates()

### define constants

g_up = 3
g_low = 1
h = 6.626e-34
k_boltzmann = 1.38e-23
m = 1.66e-27
T = 16.9
nu = 453521850000
c = 299792458
R.A_10 = 6.24e-4  # from CDMS
R.B_10 = c**3*R.A_10/8/np.pi/h/nu**3
R.B_01 = 3*R.B_10
TIon = 30.6
mIon = 14
a = 0.5
R.k3_0 = 1.7e-30

### calculate constants for simulation

#c1 = 1/CD.A_trap/c/CD.alpha/np.pi
#c2 = 4.3242e-11/R.B_10/c1
#c4 = g_up/g_low
#c5 = np.exp(-h*nu/k_boltzmann/T)

### calculate LIICG signal

def Simulation_Vary_He():
    P = 2e-5
    sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)
    gamma = 5.5e7*np.sqrt(P)
    z = 1j*gamma/(sigma*np.sqrt(2))
    norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
    c1 = 1/CD.A_trap/c*norm
    c2 = 4.3242e-11/R.B_10/c1
    c4 = g_up/g_low
    c5 = np.exp(-h*nu/k_boltzmann/T)

    n_He = np.arange(1e12, 1e18, 1e12)
    LIICG = np.zeros(len(n_He), dtype=float)

    for i in range(len(n_He)):
        x = P/n_He[i]
        LIICG[i] = c4*(1-c5)*(R.k3_0-a*R.k3_0)/(R.k3_0*(1+c4)+ a*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a*R.k3_0*c2*c4*c5*(1+c4*c5)))
    plt.semilogx()
    plt.xlabel("helium number density [cm${-3}$]", fontdict=F.font2)
    plt.ylabel("cluster depletion signal [%]", fontdict=F.font2)
    plt.plot(n_He, LIICG*100, 'k')
    path = "D:\Daten\Dokumente\SimDaten\_NewPlots\LIICG_DependenceHe_NumSimu.png"
    plt.savefig(path, format='png', dpi=600)
    plt.show()

def Simulation_Vary_P():
    P = np.arange(0, 2e-5, 2e-7)
    n_He = 5e14
    LIICG = np.zeros(len(P), dtype=float)

    for i in range(len(P)):
        sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)
        gamma = 5.5e7*np.sqrt(P[i])
        z = 1j*gamma/(sigma*np.sqrt(2))
        norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
        c1 = 1/CD.A_trap/c*norm
        c2 = 4.3242e-11/R.B_10/c1
        c4 = g_up/g_low
        c5 = np.exp(-h*nu/k_boltzmann/T)
        x = P[i]/n_He
        LIICG[i] = c4*(1-c5)*(R.k3_0-a*R.k3_0)/(R.k3_0*(1+c4)+ a*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a*R.k3_0*c2*c4*c5*(1+c4*c5)))
    plt.xlabel("THz power [%]", fontdict=F.font2)
    plt.ylabel("cluster depletion signal [%]", fontdict=F.font2)
    path = "D:\Daten\Dokumente\SimDaten\_NewPlots\LIICG_DependenceP_NumSimu.png"
    plt.plot(P/2e-5*100, LIICG*100, 'k')
    plt.savefig(path, format='png', dpi=600)
    plt.show()

def Simulation_Vary_P_Data():
    a = np.arange(0.2, 0.4, 0.01)
    P = np.arange(1e-9, 3.5e-6, 1e-7)
    n_He = 4.87e14
    LIICG = np.zeros(len(P), dtype=float)

    for j in range(len(a)):
        for i in range(len(P)):
            sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)
            gamma = 4.9e7*np.sqrt(P[i])
            z = 1j*gamma/(sigma*np.sqrt(2))
            norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
            c1 = 1/CD.A_trap/c*norm
            c2 = 4.3242e-11/R.B_10/c1
            c4 = g_up/g_low
            c5 = np.exp(-h*nu/k_boltzmann/T)
            x = P[i]/n_He
            LIICG[i] = c4*(1-c5)*(R.k3_0-a[j]*R.k3_0)/(R.k3_0*(1+c4)+ a[j]*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a[j]*R.k3_0*c2*c4*c5*(1+c4*c5)))
        #plt.semilogx()
        plt.plot(P/max(P)*100, LIICG*100, 'k')
        file1 = "D:\Daten\Dokumente\SimDaten\_Measurements\Meas_Unfoccussed_high.txt"
        x1, y1 = np.loadtxt(file1, usecols=(0, 1), unpack=True)
        plt.plot(x1, y1, color="k", marker='o', linestyle="None")
        x_ticks = [0]
        x_pos = [0]
        x_max = max(P)
        for i in range(4):
            #print(i)
            x_value = 100/4
            x_pos.append(x_value*(i+1))
            x_ticks.append(x_value*(i+1))
        plt.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
        plt.xticks(x_pos, x_ticks)
        plt.xlabel("THz power [%]", fontdict=F.font2)
        plt.ylabel("cluster depletion signal [%]", fontdict=F.font2)
        path = "D:\Daten\Dokumente\SimDaten\_NewPlots\Fit_MeasUnfocussedHigh_" + str(a[j]) + ".png"
        plt.savefig(path, format='png', dpi=600)
        plt.close()

def Simualtion_NoVariation():

    P = 2e-5
    n_He = 1.7e14
    LIICG = 0
    sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)
    gamma = 5.5e7*np.sqrt(P)
    z = 1j*gamma/(sigma*np.sqrt(2))
    norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
    c1 = 1/CD.A_trap/c*norm
    c2 = 7.5232e-11/R.B_10/c1
    c4 = g_up/g_low
    c5 = np.exp(-h*nu/k_boltzmann/T)
    x = P/n_He
    LIICG = c4*(1-c5)*(R.k3_0-a*R.k3_0)/(R.k3_0*(1+c4)+ a*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a*R.k3_0*c2*c4*c5*(1+c4*c5)))
    print(LIICG)

#Simulation_Vary_He()
#Simulation_Vary_P()
Simualtion_NoVariation()
#Simulation_Vary_P_Data()