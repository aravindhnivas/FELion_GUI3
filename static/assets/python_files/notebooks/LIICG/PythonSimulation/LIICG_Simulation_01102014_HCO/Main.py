from xml.etree.ElementInclude import include
from Tools.Scripts.find_recursionlimit import check_limit

__author__ = 'kluge_admin'


### import packages ###

import numpy as np
import Kinetic_Simualtion
import time as t
import os.path as os
import matplotlib.pyplot as plt
from Class_Definitions import Ions
from Class_Definitions import Conditions
from Class_Definitions import Ratecoefficients
from Class_Definitions import Time
from Class_Definitions import Fonts
from Class_Definitions import Rates

### define font dictionary for text and labels ###

### define abbreviation for objects ###

I = Ions()
CD = Conditions()
R = Ratecoefficients()
F = Fonts()
T = Time()
RA = Rates()

### set conditions for running simulation ###

main_dir = "D:\Daten\Dokumente\SimDaten\_NewPlots"

def simulation_multiple():
    density = (1e13, 5e13, 1e14, 5e14)
    variable2 = (0.0, 0.2, 0.4, 0.6, 0.8)
    variable = np.arange(0.01, 1, 0.02)

    t_1 = t.clock()

    for k in range(len(density)):
        for i in range(len(variable2)):
            LIICG_signal = np.zeros(len(variable), dtype=float)
            main_filename = ("LIICG_Variation_THzPower_a=" + str(variable2[i]) + "n_He=" + str(density[k]) + ".png")
            main_path = os.join(main_dir, main_filename)
            for j in range(len(variable)):
                conditions = [variable[j]*5e-6, 0.5, 400, 10, density[k], variable2[i]]
                # conditions[P_THZ[W], branching ratio CD_0/CD_1 backward reaction, trap time [ms], trap temp[K], He density [cm^-3], a]
                Kinetic_Simualtion.simulation(conditions, RA, R, CD, I, T, j)
                LIICG_signal[j] = I.LIICG
                print(str(density[k]) + " : " + str(i+1) + " von " + str(len(variable2)) + " / " + str(j+1) + " von " + str(len(variable)))
            plt.plot(variable*100, LIICG_signal, 'r')
            plt.xlabel("THz Power in %", fontdict=F.font2)
            plt.ylabel("LIICG Signal in %", fontdict=F.font2)
            x = plt.xlim()
            y = plt.ylim()
            plt.text(x[0]+(x[1]-x[0])*0.5, y[0]+(y[1]-y[0])*0.45, "He density: " + str(conditions[4]) + " cm^-3", fontdict=F.font2)
            plt.text(x[0]+(x[1]-x[0])*0.5, y[0]+(y[1]-y[0])*0.40, "trap temp: " + str(conditions[3]) + " K", fontdict=F.font2)
            plt.text(x[0]+(x[1]-x[0])*0.5, y[0]+(y[1]-y[0])*0.35, "branching ratio: " + str(conditions[1]), fontdict=F.font2)
            plt.text(x[0]+(x[1]-x[0])*0.5, y[0]+(y[1]-y[0])*0.30, "THz Power: " + str(conditions[0]) + " W", fontdict=F.font2)
            plt.text(x[0]+(x[1]-x[0])*0.5, y[0]+(y[1]-y[0])*0.25, "ratio k3_1/k3_0: " + str(conditions[5]), fontdict=F.font2)
            plt.title("THz Power Dependence of LIICG-signal of CD+", fontdict=F.font1)
            plt.savefig(main_path, format='png', dpi=600)
            plt.close()
            file = open("D:\Daten\SimDaten\LIICG\LIICG_Variation_THzPower_a=" + str(variable2[i]) + "n_He=" + str(density[k]) + ".txt", "w")
            for s in range(len(LIICG_signal)):
                file.write(str(variable[s]) + "\t")
                file.write(str(LIICG_signal[s]) + "\n")
            file.close()


    t_2 = t.clock()
    runtime = t_2-t_1

    print(runtime)

def simulation_single():

    t_1 = t.clock()

    variable = np.arange(0.0, 1, 0.2)
    density = 5e14
    variable2 = 0.0
    LIICG_signal = np.zeros(len(variable), dtype=float)
    main_filename = ("LIICG_Variation_TrapTime_a=" + str(variable2) + "n_He=" + str(density) + ".png")
    main_path = os.join(main_dir, main_filename)
    for j in range(len(variable)):
        conditions = [1e-5, 0.5, variable[j], 4, density, variable2]
        # conditions[P_THZ[W], branching ratio CD_0/CD_1 backward reaction, trap time [ms], trap temp[K], He density [cm^-3], a]
        Kinetic_Simualtion.simulation(conditions, RA, R, CD, I, T, j)
        LIICG_signal[j] = I.LIICG
        print(str(density) + " : " + str(1) + " von " + str(1) + " / " + str(j+1) + " von " + str(len(variable)))
    file1 = "D:\Daten\Dokumente\SimDaten\_Measurements\Meas_Unfoccussed_low.txt"
    x1, y1 = np.loadtxt(file1, usecols=(0, 1), unpack=True)
    plt.plot(x1, y1, color="k", marker='o', linestyle="None")
    plt.plot(variable*100, LIICG_signal*100, 'k')
    plt.xlabel("Trap Time in ms", fontdict=F.font2)
    plt.ylabel("Cluster Depletion Signal in %", fontdict=F.font2)
    x = plt.xlim()
    y = plt.ylim()
    plt.savefig(main_path, format='png', dpi=600)
    plt.show()
    file = open("D:\Daten\SimDaten\LIICG\LIICG_Variation_TrapTime_a=" + str(variable2) + "n_He=" + str(density) + ".txt", "w")
    for s in range(len(LIICG_signal)):
        file.write(str(variable[s]) + "\t")
        file.write(str(LIICG_signal[s]) + "\n")
    file.close()

    t_2 = t.clock()
    runtime = t_2-t_1

    print(runtime)

def simulation_single_data():

    t_1 = t.clock()

    a = np.arange(0.20, 0.25, 0.01)
    density = 4.87e14
    P_THz = 3.5e-6
    TrapTime = 600
    Temp = 5.7
    TIon = 12.3
    mIon = 14
    for i in range(len(a)):
        variable = np.arange(0.0, 1, 0.02)
        LIICG_signal = np.zeros(len(variable), dtype=float)
        main_filename = ("Fit_MeasUnocussedHigh_Num_a=" + str(a[i]) + ".png")
        main_path = os.join(main_dir, main_filename)
        for j in range(len(variable)):
            conditions = [variable[j]*P_THz, 0.5, TrapTime, Temp, density, a[i], TIon, mIon]
            # conditions[P_THZ[W], branching ratio CD_0/CD_1 backward reaction, trap time [ms], trap temp[K], He density [cm^-3], a]
            Kinetic_Simualtion.simulation(conditions, RA, R, CD, I, T, j)
            LIICG_signal[j] = I.LIICG
            print(str(density) + " : " + str(1) + " von " + str(1) + " / " + str(j+1) + " von " + str(len(variable)) + "-" + str(a[i]))
        file1 = "D:\Daten\Dokumente\SimDaten\_Measurements\Meas_Unfoccussed_high.txt"
        x1, y1 = np.loadtxt(file1, usecols=(0, 1), unpack=True)
        plt.plot(x1, y1, color="k", marker='o', linestyle="None")
        plt.plot(variable*100, LIICG_signal, 'k')
        x = plt.xlim()
        y = plt.ylim()
        plt.xlabel("THz power [%]", fontdict=F.font2)
        plt.ylabel("cluster depletion signal [%]", fontdict=F.font2)
        plt.savefig(main_path, format='png', dpi=600)
        plt.close()
        file = open("D:\Daten\Dokumente\SimDaten\LIICG\LIICG_Variation_THzPower_a=" + str(a[i]) + "_n_He=" + str(density) + "_Time=" + str(TrapTime) + "_Temp=" + str(Temp) + ".txt", "w")
        for s in range(len(LIICG_signal)):
            file.write(str(variable[s]) + "\t")
            file.write(str(LIICG_signal[s]) + "\n")
        file.close()

    t_2 = t.clock()
    runtime = t_2-t_1

    print(runtime)


def simulation_NoVariation():

    t_1 = t.clock()

    density = 2.5e14
    a = 0.4
    P_THz = 1e-5
    TrapTime = 600
    Temp = 5.3
    TIon = 15
    mIon = 29
    LIICG_signal = np.zeros(1, dtype=float)
    conditions = [P_THz, 0.5, TrapTime, Temp, density, a, TIon, mIon]
    # conditions[P_THZ[W], branching ratio CD_0/CD_1 backward reaction, trap time [ms], trap temp[K], He density [cm^-3], a]
    Kinetic_Simualtion.simulation(conditions, RA, R, CD, I, T, 1)
    LIICG_signal[0] = I.LIICG
    print(str(density) + " : " + str(1) + " von " + str(1) + " / " + str(1) + " von " + str(1))
    file = open("D:\Daten\Dokumente\SimDaten\LIICG\HCO_LIICG_THzPower=" + str(conditions[0]) +"_a=" + str(a) + "_n_He=" + str(density) + "_TrapTime=" + str(conditions[2]) +  "_Temp=" + str(conditions[3]) + "b.txt", "w")
    for s in range(len(LIICG_signal)):
        file.write(str(conditions[0]) + "\t")
        file.write(str(LIICG_signal[s]) + "\n")
    file.close()
    #print(LIICG_signal[0])
    t_2 = t.clock()
    runtime = t_2-t_1

    #print(runtime)
    print(LIICG_signal)

def simulation_VariationA():

    t_1 = t.clock()

    density = 2.5e14
    a = [0.0, 0.5, 0.6, 0.62, 0.64, 0.66, 0.68, 0.70, 0.8]
    P_THz = 1e-5
    TrapTime = 600
    Temp = 5.3
    TIon = 15
    mIon = 29
    LIICG_signal = np.zeros(len(a), dtype=float)
    for i in range(len(a)):
        conditions = [P_THz, 0.5, TrapTime, Temp, density, a[i], TIon, mIon]
        # conditions[P_THZ[W], branching ratio CD_0/CD_1 backward reaction, trap time [ms], trap temp[K], He density [cm^-3], a]
        Kinetic_Simualtion.simulation(conditions, RA, R, CD, I, T, 1)
        LIICG_signal[i] = I.LIICG
        print(str(a[i]) + " : " + str(LIICG_signal[i]))
        #file = open("D:\Daten\Dokumente\SimDaten\LIICG\LIICG_THzPower=" + str(conditions[0]) +"_a=" + str(a) + "_n_He=" + str(density) + "_TrapTime=" + str(conditions[2]) +  "_Temp=" + str(conditions[3]) + "b.txt", "w")
        #for s in range(len(LIICG_signal)):
        #    file.write(str(conditions[0]) + "\t")
        #    file.write(str(LIICG_signal[s]) + "\n")
        #file.close()
    t_2 = t.clock()
    runtime = t_2-t_1
    print(runtime)
    print(LIICG_signal)


### Choose which type of simulation you want to run

#simulation_multiple()
#simulation_single()
#simulation_single_data()
simulation_NoVariation()
#simulation_VariationA()