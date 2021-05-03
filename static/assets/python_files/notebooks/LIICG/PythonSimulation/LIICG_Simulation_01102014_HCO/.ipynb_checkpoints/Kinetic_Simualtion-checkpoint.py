__author__ = 'kluge_admin'

### import packages ###

import numpy as np
import matplotlib.pyplot as plt
import os.path as os
from scipy import special
from Class_Definitions import Ions
from Class_Definitions import Conditions
from Class_Definitions import Ratecoefficients
from Class_Definitions import Rates

from Class_Definitions import Time

from multiprocessing import pool

I = Ions()

CD = Conditions()
R = Ratecoefficients()
RA = Rates()
T = Time()

### define constants ###

c = 2.99792458e8
pi = 3.141599265359
h = 6.62606957e-34
k_boltzmann = 1.38e-23
m = 1.66e-27

### define time settings for simulation ###


def calculate_time_conditions(CD, T):
    T.step = 1e-3      # set timestep in ms
    T.timestep = T.step/1000  # converting step in s
    T.num_steps = int(CD.time/T.step)  # number of steps for the simulation
### calculate Einstein coefficients for the given system ###


def set_ratecoefficients(R, a):
    R.k3_0 = 1.6e-30
    R.k3_1 = a*R.k3_0
    R.k32 = 2.9e-30
    R.kCID = 3.5e-15
    R.kCID2 = 9.0e-15


def calculate_einstein_coefficients(R):
    nu = 89.2e9  # transition frequency in Hz
    R.A_10 = 4.187e-5  # from CDMS
    R.B_10 = c**3*R.A_10/8/pi/h/nu**3
    R.B_01 = 3*R.B_10

### calculate Boltzmann distribution for a given temperature ###


def calculate_occupancy(R, CD, I):
    norm = 0
    NJ = np.zeros(8, dtype=float)
    Nj = np.zeros(8)
    Energy = [0, 2.975, 8.925, 17.8497, 29.7491, 44.6228, 62.4705, 83.2919]  # typ in energy levels in cm^-1 (CDMS)
    g = [1, 3, 5, 7, 9, 11, 13, 15]

    
    for i in range(len(Energy)):
        NJ[i] = g[i]*np.exp(-Energy[i]/0.695035/CD.temp)
        norm = norm + NJ[i]

    for i in range(len(Energy)):
        Nj[i] = NJ[i]/norm

    I.N0 = Nj[0]
    
    I.N1 = Nj[1]
    
    I.N2 = Nj[2]

    ### define/calculate collisional upward/downward reaction coefficients

    R.q_01 = 10*2.2e-10  # value from Turpin et al. for CH+; linear approx
    R.q_10 = R.q_01*g[0]/g[1]*np.exp(-Energy[0]/0.695035/CD.temp)/np.exp(-Energy[1]/0.695035/CD.temp)  # calculating q_up from q_down detailed balancing
    R.q_02 = 10*0.857e-10  # value from Turpin et al. for CH+; linear approx
    R.q_20 = R.q_02*g[0]/g[2]*np.exp(-Energy[0]/0.695035/CD.temp)/np.exp(-Energy[2]/0.695035/CD.temp)  # calculating q_up from q_down detailed balancing
    R.q_12 = 10*1.152e-10  # value from Turpin et al. for CH+; linear approx
    R.q_21 = R.q_12*g[1]/g[2]*np.exp(-Energy[1]/0.695035/CD.temp)/np.exp(-Energy[2]/0.695035/CD.temp)  # calculating q_up from q_down detailed balancing
    #print(R.q_01)
    #print(R.q_02)
    #print(R.q_12)

### calculate constants for kinetic sub-functions ###


def calculate_rates(conditions, CD, RA, R, T, c, pi):
    
    sigma = 89.2e9*np.sqrt(8*conditions[6]*k_boltzmann*np.log(2)/c**2/conditions[7]/m)
    gamma = 1.5e8*np.sqrt(conditions[0])
    
    z = 1j*gamma/(sigma*np.sqrt(2))
    
    norm = (special.wofz(z)/(sigma*np.sqrt(2*np.pi))).real
    print(f"{sigma=}, {gamma=}, {norm=}\n{conditions}" )
    #print(norm)
    #norm = 1/pi/1.2e6 # Normierung für Lorentz, da Linien verbreitert sind. Gemessene Linienbreite aus Experiment
    # Normalization for Lorentz, since lines are broadened. Measured line width from experiment
    RA.Rate_B_01 = R.B_01*CD.P_THz/CD.A_trap/c*norm*T.timestep
    #print(RA.Rate_B_01/T.timestep)
    RA.Rate_B_10 = R.B_10*CD.P_THz/CD.A_trap/c*norm*T.timestep
    #print(RA.Rate_B_10/T.timestep)
    RA.Rate_A_10 = R.A_10*T.timestep
    #print(RA.Rate_A_10)
    RA.Rate_k3_0 = R.k3_0*CD.n_He*CD.n_He*T.timestep
    #print(RA.Rate_k3_0)
    RA.Rate_k3_1 = R.k3_1*CD.n_He*CD.n_He*T.timestep
    #print(RA.Rate_k3_1)
    RA.Rate_k32 = R.k32*CD.n_He*CD.n_He*T.timestep
    #print(RA.Rate_k32)
    RA.Rate_K_CID = R.kCID*CD.n_He*T.timestep
    #print(RA.Rate_K_CID)
    RA.Rate_K_CID2 = R.kCID2*CD.n_He*T.timestep
    #print(RA.Rate_K_CID2)
    RA.Rate_q_01 = R.q_01*CD.n_He*T.timestep
    #print(RA.Rate_q_up)
    RA.Rate_q_10 = R.q_10*CD.n_He*T.timestep
    #print(RA.Rate_q_down)
    RA.Rate_q_20 = R.q_20*CD.n_He*T.timestep
    RA.Rate_q_02 = R.q_02*CD.n_He*T.timestep
    RA.Rate_q_21 = R.q_21*CD.n_He*T.timestep
    RA.Rate_q_12 = R.q_12*CD.n_He*T.timestep

### define sub functions for kinetic simulation / with and without light ###


def kinetic_light_on(j, I, CD, RA):
    I.CD_0_on[j] = I.CD_0_on[j-1]-I.CD_0_on[j-1]*RA.Rate_k3_0+I.CDHe_on[j-1]*RA.Rate_K_CID*CD.p\
                    - I.CD_0_on[j-1]*RA.Rate_B_01+I.CD_1_on[j-1]*RA.Rate_B_10\
                    + I.CD_1_on[j-1]*RA.Rate_A_10-I.CD_0_on[j-1]*RA.Rate_q_01+I.CD_1_on[j-1]*RA.Rate_q_10\
                    - I.CD_0_on[j-1]*RA.Rate_q_02+I.CD_2_on[j-1]*RA.Rate_q_20
    I.CD_1_on[j] = I.CD_1_on[j-1]-I.CD_1_on[j-1]*RA.Rate_k3_1+I.CDHe_on[j-1]*RA.Rate_K_CID*(1-CD.p)\
                    + I.CD_0_on[j-1]*RA.Rate_B_01-I.CD_1_on[j-1]*RA.Rate_B_10\
                    - I.CD_1_on[j-1]*RA.Rate_A_10+I.CD_0_on[j-1]*RA.Rate_q_01-I.CD_1_on[j-1]*RA.Rate_q_10\
                    - I.CD_1_on[j-1]*RA.Rate_q_12+I.CD_2_on[j-1]*RA.Rate_q_21
    I.CD_2_on[j] = I.CD_2_on[j-1]+I.CD_0_on[j-1]*RA.Rate_q_02-I.CD_2_on[j-1]*RA.Rate_q_20\
                     +I.CD_1_on[j-1]*RA.Rate_q_12-I.CD_2_on[j-1]*RA.Rate_q_21
    I.CDHe_on[j] = I.CDHe_on[j-1]+I.CD_0_on[j-1]*RA.Rate_k3_0-I.CDHe_on[j-1]*RA.Rate_K_CID*CD.p\
                    + I.CD_1_on[j-1]*RA.Rate_k3_1-I.CDHe_on[j-1]*RA.Rate_K_CID*(1-CD.p)\
                    - I.CDHe_on[j-1]*RA.Rate_k32+I.CDHe2_on[j-1]*RA.Rate_K_CID2
    I.CDHe2_on[j] = I.CDHe2_on[j-1]+I.CDHe_on[j-1]*RA.Rate_k32-I.CDHe2_on[j-1]*RA.Rate_K_CID2
    I.Sum_on[j] = I.CD_0_on[j]+I.CD_1_on[j]+I.CDHe_on[j]+I.CDHe2_on[j]

def kinetic_light_off(j, I, CD, RA):
    I.CD_0_off[j] = I.CD_0_off[j-1]-I.CD_0_off[j-1]*RA.Rate_k3_0+I.CDHe_off[j-1]*RA.Rate_K_CID*CD.p\
                    + I.CD_1_off[j-1]*RA.Rate_A_10-I.CD_0_off[j-1]*RA.Rate_q_01+I.CD_1_off[j-1]*RA.Rate_q_10\
                    - I.CD_0_off[j-1]*RA.Rate_q_02+I.CD_2_off[j-1]*RA.Rate_q_20
    I.CD_1_off[j] = I.CD_1_off[j-1]-I.CD_1_off[j-1]*RA.Rate_k3_1+I.CDHe_off[j-1]*RA.Rate_K_CID*(1-CD.p)\
                    - I.CD_1_off[j-1]*RA.Rate_A_10+I.CD_0_off[j-1]*RA.Rate_q_01-I.CD_1_off[j-1]*RA.Rate_q_10\
                    - I.CD_1_off[j-1]*RA.Rate_q_12+I.CD_2_off[j-1]*RA.Rate_q_21
    I.CD_2_off[j] = I.CD_2_off[j-1]+I.CD_0_off[j-1]*RA.Rate_q_02-I.CD_2_off[j-1]*RA.Rate_q_20\
                    +I.CD_1_off[j-1]*RA.Rate_q_12-I.CD_2_off[j-1]*RA.Rate_q_21
    I.CDHe_off[j] = I.CDHe_off[j-1]+I.CD_0_off[j-1]*RA.Rate_k3_0-I.CDHe_off[j-1]*RA.Rate_K_CID*CD.p\
                    + I.CD_1_off[j-1]*RA.Rate_k3_1-I.CDHe_off[j-1]*RA.Rate_K_CID*(1-CD.p)\
                    - I.CDHe_off[j-1]*RA.Rate_k32+I.CDHe2_off[j-1]*RA.Rate_K_CID2
    I.CDHe2_off[j] = I.CDHe2_off[j-1]+I.CDHe_off[j-1]*RA.Rate_k32-I.CDHe2_off[j-1]*RA.Rate_K_CID2
    I.Sum_off[j] = I.CD_0_off[j]+I.CD_1_off[j]+I.CDHe_off[j]+I.CDHe2_off[j]

def plot_figure(I, var1, var2):
    plot_dir = "D:\Daten\Dokumente"
    plot_filename_on = "LIICG_Variation_THzPower_KineticPlot_on_HeDensity=" + str(var1) + "_a=" + str(var2) + ".png"
    plot_path = os.join(plot_dir, plot_filename_on)
    plt.plot(I.CDHe_on, 'r')
    plt.plot(I.CD_0_on, 'g')
    plt.plot(I.CD_1_on, 'b')
    plt.savefig(plot_path, format='png')
    plt.close()
    plot_filename_off = "LIICG_Variation_THzPower_KineticPlot_off_HeDensity=" + str(var1) + "_a=" + str(var2) + ".png"
    plot_path = os.join(plot_dir, plot_filename_off)
    plt.plot(I.CDHe_off, 'r')
    plt.plot(I.CD_0_off, 'g')
    plt.plot(I.CD_1_off, 'b')
    plt.savefig(plot_path, format='png')
    plt.close()

def simulation(conditions, RA, R, CD, I, T, j):
    
    ### set conditions for simulation ###
    CD.P_THz = conditions[0]  # THz light intensity in W
    CD.p = conditions[1]  # propability p that CID creates CD+ in the rotational state J=0
    CD.time = conditions[2]    # set simulation time in ms
    CD.temp = conditions[3]       # set trap temperature in K 
    CD.n_He = conditions[4]    # He number density in the trap
    a = conditions[5]

    set_ratecoefficients(R, a)  # Set and calculate ratecoefficients
    calculate_einstein_coefficients(R)  # calculate Einstein coefficients
    calculate_time_conditions(CD, T)  # calculate time conditions

    ### initialize arrays for different ion types ###

    I.CD_0_on = np.zeros(T.num_steps, dtype=float)   # init array for CD+ ions in rotational state J=0, with THz on
    I.CD_0_off = np.zeros(T.num_steps, dtype=float)  # init array for CD+ ions in rotational state J=0, with THz off
    I.CD_1_on = np.zeros(T.num_steps, dtype=float)   # init array for CD+ ions in rotational state J=1, with THz on
    I.CD_1_off = np.zeros(T.num_steps, dtype=float)  # init array for CD+ ions in rotational state J=1, with THz off
    I.CD_2_on = np.zeros(T.num_steps, dtype=float)   # init array for CD+ ions in rotational state J=2 , with THz on
    I.CD_2_off = np.zeros(T.num_steps, dtype=float)  # init array for CD+ ions in rotational state J=2, with THz off
    I.CDHe_on = np.zeros(T.num_steps, dtype=float)   # init array for HeCD+ ions / all rot. states, with THz on
    I.CDHe_off = np.zeros(T.num_steps, dtype=float)   # init array for HeCD+ ions / all rot. states, with THz off
    I.CDHe2_on = np.zeros(T.num_steps, dtype=float)  # init array for He2CD+ ions / all rot. states, with THz on
    I.CDHe2_off = np.zeros(T.num_steps, dtype=float)  # init array for He2CD+ ions / all rot. states, with THz off
    I.Sum_on = np.zeros(T.num_steps, dtype=float)    # init array for sum of all ions in the system, with THz on
    I.Sum_off = np.zeros(T.num_steps, dtype=float)    # init array for sum of all ions in the system, with THz off

    ### calculate rates for given conditions ###

    calculate_occupancy(R, CD, I)
    calculate_rates(conditions, CD, RA, R, T, c, pi)

    #### define/calculate initial conditions for ion species ###

    num_ions = 1000
    I.CD_0_on[0] = I.N0*num_ions
    I.CD_1_on[0] = I.N1*num_ions
    I.CD_2_on[0] = I.N2*num_ions
    I.CDHe_on[0] = 0
    I.CDHe2_on[0] = 0
    I.Sum_on[0] = I.CD_0_on[0]+I.CD_1_on[0]+I.CD_2_on[0]+I.CDHe_on[0]+I.CDHe2_on[0]
    I.CD_0_off[0] = I.N0*num_ions
    I.CD_1_off[0] = I.N1*num_ions
    I.CD_2_off[0] = I.N2*num_ions
    I.CDHe_off[0] = 0
    I.CDHe2_off[0] = 0
    I.Sum_off[0] = I.CD_0_off[0]+I.CD_1_off[0]+I.CD_2_off[0]+I.CDHe_off[0]+I.CDHe2_off[0]

    ### kinetic simulation ###
    for i in range(1, T.num_steps):
        kinetic_light_on(i, I, CD, RA)
        kinetic_light_off(i, I, CD, RA)
        factor = 1  # Choose at which power level the levelpop files should be created
        
        """
        if CD.P_THz == factor*conditions[0]:
            file = open("./HCOLevelPopulation_on_THzPower=" + str(CD.P_THz) +"_a=" + str(a) + "_n_He=" + str(CD.n_He) + "_TrapTime=" + str(CD.time) + "_Temp=" + str(CD.temp) + ".txt", "w")
            for k in range(len(I.Sum_on)):
                file.write(str(I.CD_0_on[k]) + "\t")
                file.write(str(I.CD_1_on[k]) + "\t")
                file.write(str(I.CD_2_on[k]) + "\t")
                file.write(str(I.CDHe_on[k]) + "\t")
                file.write(str(I.CDHe2_on[k]) + "\t")
                file.write(str(I.Sum_on[k]) + "\n")
            file.close()
            file = open("./HCOLevelPopulation_off_THzPower=" + str(CD.P_THz) +"_a=" + str(a) + "_n_He=" + str(CD.n_He) + "_TrapTime=" + str(CD.time) + "_Temp=" + str(CD.temp) + ".txt", "w")
            for k in range(len(I.Sum_off)):
                file.write(str(I.CD_0_off[k]) + "\t")
                file.write(str(I.CD_1_off[k]) + "\t")
                file.write(str(I.CD_2_off[k]) + "\t")
                file.write(str(I.CDHe_off[k]) + "\t")
                file.write(str(I.CDHe2_off[k]) + "\t")
                file.write(str(I.Sum_off[k]) + "\n")
            file.close()
        """
        
    I.LIICG = (I.CDHe_off[T.num_steps-1]-I.CDHe_on[T.num_steps-1])/I.CDHe_off[T.num_steps-1]*100
    
    
    #print(I.CDHe2_on[T.num_steps-1]/10)
    
    #print(I.CDHe2_off[T.num_steps-1]/10)