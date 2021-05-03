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

g_up = 2
g_low = 2
h = 6.626e-34
k_boltzmann = 1.38e-23
m = 1.66e-27
T = 5.7
nu = 117.6923e9
c = 299792458
R.A_10 = 4.31e-5  # from CDMS
R.B_10 = c**3*R.A_10/8/np.pi/h/nu**3
R.B_01 = g_up/g_low*R.B_10
TIon = 12.3
mIon = 28
a = 0.55
R.k3_0 = 0.9e-30
R.k10 = 5e-11

### calculate constants for simulation

#c1 = 1/CD.A_trap/c/CD.alpha/np.pi
#c2 = 4.3242e-11/R.B_10/c1
#c4 = g_up/g_low
#c5 = np.exp(-h*nu/k_boltzmann/T)

### calculate LIICG signal

def Simulation_Vary_He():
    P = 2e-5
    sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)/(np.sqrt(8*np.log(2)))
    gamma = 5.5e7*np.sqrt(P)/2
    z = 1j*gamma/(sigma*np.sqrt(2))
    norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
    c1 = 1/CD.A_trap/c*norm
    c2 = R.k10/R.B_10/c1
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
    path = "LIICG_DependenceHe_NumSimu.png"
    plt.savefig(path, format='png', dpi=600)
    plt.show()

def Simulation_N_Vary_He():
    P = 20e-6
    a=0.53
    sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)/(np.sqrt(8*np.log(2)))
    gamma = 5.5e7*np.sqrt(P)/2
    z = 1j*gamma/(sigma*np.sqrt(2))
    norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
    c1 = 1/CD.A_trap/c*norm
    c2 = R.k10/R.B_10/c1
    c4 = g_up/g_low
    c5 = np.exp(-h*nu/k_boltzmann/T)

    n_He = np.logspace(12, 18, num=200, endpoint=True, base=10.0, dtype=float)
    LIICG = np.zeros(len(n_He), dtype=float)
    Nratio = np.zeros(len(n_He), dtype=float)

    for i in range(len(n_He)):
        x = P/n_He[i]
        Nratio[i] = c4 * (x + c2 * c5) / (x + c2)
        LIICG[i] = c4*(1-c5)*(R.k3_0-a*R.k3_0)/(R.k3_0*(1+c4)+ a*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a*R.k3_0*c2*c4*c5*(1+c4*c5)))
    plt.semilogx()
    plt.xlabel("helium number density [cm${-3}$]", fontdict=F.font2)
    plt.ylabel("N1/N0 ratio", fontdict=F.font2)
    plt.plot(n_He, Nratio, 'k')
    path = "Nratio_DependenceHe_NumSimu_29E-6W_0.53.png"
    plt.savefig(path, format='png', dpi=600)
    plt.show()
    file = open('Nratio_LIICG_5.7K_20E-6W_0.53.txt','w')
    for s in range(len(n_He)):
        file.write(str(n_He[s]) + '\t')
        file.write(str(Nratio[s]) + '\t')
        file.write(str(LIICG[s]*100) + '\n')
    file.close()

def Simulation_Vary_P():
    P = np.arange(0, 2e-5, 2e-7)
    n_He = 5e14
    LIICG = np.zeros(len(P), dtype=float)

    for i in range(len(P)):
        sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)/(np.sqrt(8*np.log(2)))
        gamma = 5.5e7*np.sqrt(P)/2
        z = 1j*gamma/(sigma*np.sqrt(2))
        norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
        c1 = 1/CD.A_trap/c*norm
        c2 = R.k10/R.B_10/c1
        c4 = g_up/g_low
        c5 = np.exp(-h*nu/k_boltzmann/T)
        x[i] = P[i]/n_He
        Nratio[i] = c4 * (x + c2 * c5) / (x[i] + c2)
        LIICG[i] = c4*(1-c5)*(R.k3_0-a*R.k3_0)/(R.k3_0*(1+c4)+ a*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a*R.k3_0*c2*c4*c5*(1+c4*c5)))
    plt.xlabel("THz power [%]", fontdict=F.font2)
    plt.ylabel("cluster depletion signal [%]", fontdict=F.font2)
    path = "D:\Daten\Dokumente\SimDaten\_NewPlots\LIICG_DependenceP_NumSimu.png"
    plt.plot(P/2e-5*100, LIICG*100, 'k')
#    plt.savefig(path, format='png', dpi=600)
    plt.show()
    file = open('Nratio_LIICG_5.7K_nHe=_new.txt','w')
    for s in range(len(P)):
        file.write(str(P[s]) + '\t')
        file.write(str(Nratio[s]) + '\t')
        file.write(str(LIICG[s]) + '\n')
    file.close()

def Simulation_Vary_P_Data():
    a = np.arange(0.45, 0.65, 0.01)
    P = np.arange(1e-9, 3.51e-6, 1e-7)
    n_He = 4.87e14
    LIICG = np.zeros(len(P), dtype=float)

    for j in range(len(a)):
        for i in range(len(P)):
            sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)/(np.sqrt(8*np.log(2)))
            gamma = 5.5e7*np.sqrt(P[i])/2
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
        file1 = "Meas_Unfoccussed_high.txt"
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
        path = "Figures/Fit_MeasUnFoccussed_high_" + str(a[j]) + ".png"
        plt.savefig(path, format='png', dpi=600)
        plt.close()
        file = open('Data/Nratio_LIICG_5.7K_aP_nHe=' + str(n_He) + '_' + str(a[j]) + '.txt','w')
        for s in range(len(P)):
            file.write(str(P[s]) + '\t')
            file.write(str(LIICG[s]*100) + '\n')
        file.close()

def Simualtion_NoVariation():
    g_up = 2
    g_low = 2
    h = 6.626e-34
    k_boltzmann = 1.38e-23
    m = 1.66e-27
    T = 5.7
    TIon = 12.3
    nu = 117.6923e9
    c = 299792458
    R.A_10 = 4.31e-5  # from CDMS
    R.B_10 = c**3*R.A_10/8/np.pi/h/nu**3
    R.B_01 = g_up/g_low*R.B_10
    mIon = 28
    R.k3_0 = 0.9e-30
    R.k10 = 5e-11
    a = 0.65
    P = 8.0e-5
    n_He = 4.8e14
    LIICG = 0
    sigma = nu*np.sqrt(8*TIon*k_boltzmann*np.log(2)/c**2/mIon/m)/(np.sqrt(8*np.log(2)))
    gamma = 5.5e7*np.sqrt(P)/2
    voigt = 0.5346*gamma + np.sqrt(0.2166*gamma*gamma+sigma*sigma)
    print('sigma=', sigma)
    print('gamma=', gamma)
    print('voigt=', voigt)
    z = 1j*gamma/(sigma*np.sqrt(2))
    norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
    RB01 = R.B_01*P/CD.A_trap/c*norm
    RB10 = R.B_10*P/CD.A_trap/c*norm
    c1 = 1/CD.A_trap/c*norm
    c5 = np.exp(-h*nu/k_boltzmann/T)
    R.k01 = 9.0E-10
    R.k10 = g_up/g_low * R.k01 * c5
    c2 = R.k10/R.B_10/c1
    c4 = g_up/g_low
    x = P/n_He
    LIICG = c4*(1-c5)*(R.k3_0-a*R.k3_0)/(R.k3_0*(1+c4)+ a*R.k3_0*(1+c4)*c4*c5+1/x*(R.k3_0*c2*(1+c4*c5)+a*R.k3_0*c2*c4*c5*(1+c4*c5)))
    Nratio = c4 * (x + c2 * c5) / (x + c2)
    Nratio_off = c4*c5
    Nratio_max = c4
    Rcoll=R.k10*n_He
    print('signal=',LIICG*100)
    print('Nratio=', Nratio)
    print('Nratio_off=', Nratio_off)
    print('Nratio_max=', Nratio_max)
    print('RB01=', RB01)
    print('RB10=', RB10)
    print('Rcoll=', Rcoll)
##    file = open('Data/Nratio_LIICG_a=0.35_nHe=' + str(n_He) + '_T=' + str(T) + '.txt','w')
##    file.write(str(T) + '\t')
##    file.write(str(LIICG*100) + '\t')
##    file.write(str(Nratio_off) + '\t')
##    file.write(str(Nratio) + '\n')
##    file.close()


#Simulation_Vary_He()
#Simulation_N_Vary_He()
#Simulation_Vary_P()
Simualtion_NoVariation()
#Simulation_Vary_P_Data()
#Simulation_a()
