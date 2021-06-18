__author__ = 'Monika'
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import os as sys
from glob import glob
import math as math

runprogram = 1
directory = sys.getcwd()

while runprogram == 1:
    fitokay = 0
    print("Was möchten Sie machen?")
    print("Messung fitten: 1")
    print("Programm beenden: 0")
    UserChoice = int(input("Bitte waehlen Sie: "))

    # Öffne Daten- und zugehöriges Parameterfile
    if UserChoice == 1:
        DataFilesInDir = glob(directory + "/*_timescan.txt")
        ParameterFilesInDir = glob(directory + "/*_parameter.txt")
        for i in range(len(DataFilesInDir)):
                print(str(i) + " : " + sys.path.basename(DataFilesInDir[i]))
        FileNumber = input("Welche Datei moechten Sie plotten? Geben Sie die Nummer der entsprechenden Datei ein: ")
        datafile = open(DataFilesInDir[int(FileNumber)], 'r')
        try:
            parameterfile = open(ParameterFilesInDir[int(FileNumber)], 'r')
        except IndexError:
            print("Zugehoeriges Parameterfile existiert nicht.")
            break
        except FileNotFoundError:
            print("Zugehoeriges Parameterfile existiert nicht.")
        # Erzeuge Variablen aus der Variablenliste und weise Werte aus der Parameterdatei zu

        ListofParameters = ("Temperature", "Timesteps", "NumberOfMasses", "SimulationTime", "StartTimeStep", "n_He", "k01", "k12", "k23", "k10", "k21", "k32", "k34", "k43", "k54", "k45")
        parameter_lines = parameterfile.readlines()
        parameters = []
        parameterlist = {}

        for i in parameter_lines:
            parameters.append(i.strip().split())

        for i in range(len(parameters)):
            parameterlist[parameters[i][0]] = parameters[i][1]

        for i in ListofParameters:
            try:
                locals()[i] = int(parameterlist[i])  # erzeugt Variablen mit den Namen in der oben definierten Liste
            except KeyError:
                print("Warning: " + i + " is not defined in the parameter file")  # Gibt eine Warnung aus, wenn die Variable nicht in der Parameterdatei vorhanden ist
            except ValueError:
                try:
                    locals()[i] = float(parameterlist[i])  # Wenn der Wert der Variablen kein Integer ist, versucht das Programm den Wert als Float einzulesen
                except ValueError:
                    print("Error: parameter " + i + "has not the correct format")
        print(NumberOfMasses)
        NumberOfColumns = NumberOfMasses + 2  # Number of columns including time and sum

        #Bedingungen Messung
        t = 0.001               #Zeitintervall in s

        # Remove header files
        headerlength = NumberOfMasses + 5
        for i in range(0, headerlength):
            test = datafile.readline()

        # Initialize data array (first index number of time points
        # Second index masses plus time plus sum (automatize)
        data = np.zeros((Timesteps, NumberOfColumns))

        # read in lines after header and add to array
        for i in range(0, Timesteps):
            line = datafile.readline()
            line = line.strip()
            data[i] = line.split()

        potenz = int(math.log10(data.max()))
        x_max = 10**(potenz+1)

        if NumberOfMasses == 2:
            while fitokay == 0:
                CD_0 = data[StartTimeStep][NumberOfMasses + 1]
                CDHe_0 = 0
                summe_0 = CD_0 + CDHe_0
                CD = np.zeros(SimulationTime)
                CDHe = np.zeros(SimulationTime)
                summe = np.zeros(SimulationTime)
                CD[0] = CD_0
                CDHe[0] = CDHe_0
                summe[0] = summe_0
                for i in range(1, SimulationTime):
                    CD[i] = CD[i-1] + k10 * CDHe[i-1] * n_He * t - k01 * CD[i-1] * n_He * n_He * t
                    CDHe[i] = CDHe[i-1] + k01 * n_He * n_He * CD[i-1] * t - k10 * CDHe[i-1] * n_He * t
                    summe[i] = CD[i] + CDHe[i]

                summe_meas = np.zeros(Timesteps)
                summe_meas = data[:, 1] + data[:, 2]
                plt.figure(1) #Initialisierung Plot1

                font = {'family' : 'arial',
                        'color'  : 'red',
                        'weight' : 'normal',
                        'size'   : 14,
                        }

                plt.plot(CD, 'r')
                plt.plot(data[:, 0], data[:, 1], 'ro')
                #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe, 'b')
                plt.plot(data[:, 0], data[:, 2], 'bo')
                #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                plt.plot(summe, 'k')
                plt.plot(data[:, 0], summe_meas, 'ko')
                #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                plt.semilogy()
                plt.xlabel('reaction time [ms]')
                plt.ylabel('$He_n-CD^+$')
                plt.xlim([0, SimulationTime])
                plt.ylim([0.05, x_max])
                plt.show()
                Replot = input("Erneut plotten (y/n)? : ")
                if Replot == "y":
                    fitokay = 0
                    parameterfile = open(ParameterFilesInDir[int(FileNumber)], 'r')
                    parameter_lines = parameterfile.readlines()
                    parameters = []
                    parameterlist = {}

                    for i in parameter_lines:
                        parameters.append(i.strip().split())

                    for i in range(len(parameters)):
                        parameterlist[parameters[i][0]] = parameters[i][1]

                    for i in ListofParameters:
                        try:
                            locals()[i] = int(parameterlist[i])  # erzeugt Variablen mit den Namen in der oben definierten Liste
                        except KeyError:
                            print("Warning: " + i + " is not defined in the parameter file")  # Gibt eine Warnung aus, wenn die Variable nicht in der Parameterdatei vorhanden ist
                        except ValueError:
                            try:
                                locals()[i] = float(parameterlist[i])  # Wenn der Wert der Variablen kein Integer ist, versucht das Programm den Wert als Float einzulesen
                            except ValueError:
                                print("Error: parameter " + i + "has not the correct format")
                else:
                    fitokay = 1
                    Save = input("Moechten Sie den Plot speichern (y/n)? : ")
                    if Save == "y":
                        Name_parts = sys.path.basename(DataFilesInDir[int(FileNumber)]).split("_")
                        plot_name = Name_parts[0] + "_" + Name_parts[1]
                        plt.plot(CD, 'r')
                        plt.plot(data[:, 0], data[:, 1], 'ro')
                        #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe, 'b')
                        plt.plot(data[:, 0], data[:, 2], 'bo')
                        #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(summe, 'k')
                        plt.plot(data[:, 0], summe_meas, 'ko')
                        #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                        plt.semilogy()
                        plt.xlabel('reaction time [ms]')
                        plt.ylabel('$He_n-CD^+$')
                        plt.xlim([0, SimulationTime])
                        plt.ylim([0.05, x_max])
                        plt.savefig(directory + "/" + plot_name + ".png", dpi=600)
                        if sys.path.isfile(directory + "/" + plot_name + ".png") == True:
                            print("Ihre Datei wurde unter " + directory + "/" + plot_name + ".png" + " abgespeichert.")
                        else:
                            print("Fehler beim schreiben der Datei")

        elif NumberOfMasses == 3:
            while fitokay == 0:
                CD_0 = data[StartTimeStep][NumberOfMasses + 1]
                CDHe_0 = 0
                CDHe2_0 = 0
                summe_0 = CD_0 + CDHe_0 + CDHe2_0
                CD = np.zeros(SimulationTime)
                CDHe = np.zeros(SimulationTime)
                CDHe2 = np.zeros(SimulationTime)
                summe = np.zeros(SimulationTime)
                CD[0] = CD_0
                CDHe[0] = CDHe_0
                CDHe2[0] = CDHe2_0
                summe[0] = summe_0
                for i in range(1, SimulationTime):
                    CD[i] = CD[i-1] + k10 * CDHe[i-1] * n_He * t - k01 * CD[i-1] * n_He * n_He * t
                    CDHe[i] = CDHe[i-1] + k01 * n_He * n_He * CD[i-1] * t - k10 * CDHe[i-1] * n_He * t + k21 * CDHe2[i-1] * n_He * t - k12 * CDHe[i-1] * n_He * n_He * t
                    CDHe2[i] = CDHe2[i-1] + k12 * n_He * n_He * CDHe[i-1] * t - k21 * CDHe2[i-1] * n_He * t
                    summe[i] = CD[i] + CDHe[i] + CDHe2[i]

                summe_meas = np.zeros(Timesteps)
                summe_meas = data[:, 1] + data[:, 2] + data[:, 3]

                plt.figure(1)  # Initialisierung Plot 1

                font = {'family' : 'arial',
                        'color'  : 'red',
                        'weight' : 'normal',
                        'size'   : 14,
                        }

                plt.plot(CD, 'r')
                plt.plot(data[:, 0], data[:, 1], 'ro')
                #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe, 'b')
                plt.plot(data[:, 0], data[:, 2], 'bo')
                #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe2, 'g')
                plt.plot(data[:, 0], data[:, 3], 'go')
                #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                plt.plot(summe, 'k')
                plt.plot(data[:, 0], summe_meas, 'ko')
                #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                plt.semilogy()
                plt.xlabel('reaction time [ms]')
                plt.ylabel('$He_n-CD^+$')
                plt.xlim([0, SimulationTime])
                plt.ylim([0.05, x_max])
                plt.show()
                Replot = input("Erneut plotten (y/n)? : ")
                if Replot == "y":
                    fitokay = 0
                    parameterfile = open(ParameterFilesInDir[int(FileNumber)], 'r')
                    parameter_lines = parameterfile.readlines()
                    parameters = []
                    parameterlist = {}

                    for i in parameter_lines:
                        parameters.append(i.strip().split())

                    for i in range(len(parameters)):
                        parameterlist[parameters[i][0]] = parameters[i][1]

                    for i in ListofParameters:
                        try:
                            locals()[i] = int(parameterlist[i])  # erzeugt Variablen mit den Namen in der oben definierten Liste
                        except KeyError:
                            print("Warning: " + i + " is not defined in the parameter file")  # Gibt eine Warnung aus, wenn die Variable nicht in der Parameterdatei vorhanden ist
                        except ValueError:
                            try:
                                locals()[i] = float(parameterlist[i])  # Wenn der Wert der Variablen kein Integer ist, versucht das Programm den Wert als Float einzulesen
                            except ValueError:
                                print("Error: parameter " + i + "has not the correct format")
                else:
                    fitokay = 1
                    Save = input("Moechten Sie den Plot speichern (y/n)? : ")
                    if Save == "y":
                        Name_parts = sys.path.basename(DataFilesInDir[int(FileNumber)]).split("_")
                        plot_name = Name_parts[0] + "_" + Name_parts[1]
                        plt.plot(CD, 'r')
                        plt.plot(data[:, 0], data[:, 1], 'ro')
                        #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe, 'b')
                        plt.plot(data[:, 0], data[:, 2], 'bo')
                        #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe2, 'g')
                        plt.plot(data[:, 0], data[:, 3], 'go')
                        #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(summe, 'k')
                        plt.plot(data[:, 0], summe_meas, 'ko')
                        #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                        plt.semilogy()
                        plt.xlabel('reaction time [ms]')
                        plt.ylabel('$He_n-CD^+$')
                        plt.xlim([0, SimulationTime])
                        plt.ylim([0.05, x_max])
                        plt.savefig(directory + "/" + plot_name + ".png", dpi=600)
                        if sys.path.isfile(directory + "/" + plot_name + ".png") == True:
                            print("Ihre Datei wurde unter " + directory + "/" + plot_name + ".png" + " abgespeichert.")
                        else:
                            print("Fehler beim schreiben der Datei")

        elif NumberOfMasses == 4:
            while fitokay == 0:
                CD_0 = data[StartTimeStep][NumberOfMasses + 1]
                CDHe_0 = 0
                CDHe2_0 = 0
                CDHe3_0 = 0
                summe_0 = CD_0 + CDHe_0 + CDHe2_0 + CDHe3_0
                CD = np.zeros(SimulationTime)
                CDHe = np.zeros(SimulationTime)
                CDHe2 = np.zeros(SimulationTime)
                CDHe3 = np.zeros(SimulationTime)
                summe = np.zeros(SimulationTime)
                CD[0] = CD_0
                CDHe[0] = CDHe_0
                CDHe2[0] = CDHe2_0
                CDHe3[0] = CDHe3_0
                summe[0] = summe_0
                for i in range(1, SimulationTime):
                    CD[i] = CD[i-1] + k10 * CDHe[i-1] * n_He * t - k01 * CD[i-1] * n_He * n_He * t
                    CDHe[i] = CDHe[i-1] + k01 * n_He * n_He * CD[i-1] * t - k10 * CDHe[i-1] * n_He * t + k21 * CDHe2[i-1] * n_He * t - k12 * CDHe[i-1] * n_He * n_He * t
                    CDHe2[i] = CDHe2[i-1] + k12 * n_He * n_He * CDHe[i-1] * t - k21 * CDHe2[i-1] * n_He * t + k32 * CDHe3[i-1] * n_He * t - k23 * CDHe2[i-1] * n_He * n_He * t
                    CDHe3[i] = CDHe3[i-1] + k23 * n_He * n_He * CDHe2[i-1] * t - k32 * CDHe3[i-1] * n_He * t
                    summe[i] = CD[i] + CDHe[i] + CDHe2[i] + CDHe3[i]

                summe_meas = np.zeros(Timesteps)
                summe_meas = data[:, 1] + data[:, 2] + data[:, 3] + data[:, 4]

                plt.figure(1) #Initialisierung Plot1

                font = {'family' : 'arial',
                        'color'  : 'red',
                        'weight' : 'normal',
                        'size'   : 14,
                        }

                plt.plot(CD, 'r')
                plt.plot(data[:, 0], data[:, 1], 'ro')
                #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe, 'b')
                plt.plot(data[:, 0], data[:, 2], 'bo')
                #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe2, 'g')
                plt.plot(data[:, 0], data[:, 3], 'go')
                #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe3, 'm')
                plt.plot(data[:, 0], data[:, 4], 'mo')
                #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                plt.plot(summe, 'k')
                plt.plot(data[:, 0], summe_meas, 'ko')
                #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                plt.semilogy()
                plt.xlabel('reaction time [ms]')
                plt.ylabel('$He_n-CD^+$')
                plt.xlim([0, SimulationTime])
                plt.ylim([0.05, x_max])
                plt.show()
                Replot = input("Erneut plotten (y/n)? : ")
                if Replot == "y":
                    fitokay = 0
                    parameterfile = open(ParameterFilesInDir[int(FileNumber)], 'r')
                    parameter_lines = parameterfile.readlines()
                    parameters = []
                    parameterlist = {}

                    for i in parameter_lines:
                        parameters.append(i.strip().split())

                    for i in range(len(parameters)):
                        parameterlist[parameters[i][0]] = parameters[i][1]

                    for i in ListofParameters:
                        try:
                            locals()[i] = int(parameterlist[i])  # erzeugt Variablen mit den Namen in der oben definierten Liste
                        except KeyError:
                            print("Warning: " + i + " is not defined in the parameter file")  # Gibt eine Warnung aus, wenn die Variable nicht in der Parameterdatei vorhanden ist
                        except ValueError:
                            try:
                                locals()[i] = float(parameterlist[i])  # Wenn der Wert der Variablen kein Integer ist, versucht das Programm den Wert als Float einzulesen
                            except ValueError:
                                print("Error: parameter " + i + "has not the correct format")
                else:
                    fitokay = 1
                    Save = input("Moechten Sie den Plot speichern (y/n)? : ")
                    if Save == "y":
                        print(NumberOfMasses)
                        Name_parts = sys.path.basename(DataFilesInDir[int(FileNumber)]).split("_")
                        plot_name = Name_parts[0] + "_" + Name_parts[1]
                        plt.plot(CD, 'r')
                        plt.plot(data[:, 0], data[:, 1], 'ro')
                        #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe, 'b')
                        plt.plot(data[:, 0], data[:, 2], 'bo')
                        #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe2, 'g')
                        plt.plot(data[:, 0], data[:, 3], 'go')
                        #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe3, 'm')
                        plt.plot(data[:, 0], data[:, 4], 'mo')
                        #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(summe, 'k')
                        plt.plot(data[:, 0], summe_meas, 'ko')
                        #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                        plt.semilogy()
                        plt.xlabel('reaction time [ms]')
                        plt.ylabel('$He_n-CD^+$')
                        plt.xlim([0, SimulationTime])
                        plt.ylim([0.05, x_max])
                        plt.savefig(directory + "/" + plot_name + ".png", dpi=600)
                        if sys.path.isfile(directory + "/" + plot_name + ".png") == True:
                            print("Ihre Datei wurde unter " + directory + "/" + plot_name + ".png" + " abgespeichert.")
                        else:
                            print("Fehler beim schreiben der Datei")

        elif NumberOfMasses == 5:
            while fitokay == 0:
                CD_0 = data[StartTimeStep][NumberOfMasses + 1]
                CDHe_0 = 0
                CDHe2_0 = 0
                CDHe3_0 = 0
                CDHe4_0 = 0
                summe_0 = CD_0 + CDHe_0 + CDHe2_0 + CDHe3_0 + CDHe4_0
                CD = np.zeros(SimulationTime)
                CDHe = np.zeros(SimulationTime)
                CDHe2 = np.zeros(SimulationTime)
                CDHe3 = np.zeros(SimulationTime)
                CDHe4 = np.zeros(SimulationTime)
                summe = np.zeros(SimulationTime)
                CD[0] = CD_0
                CDHe[0] = CDHe_0
                CDHe2[0] = CDHe2_0
                CDHe3[0] = CDHe3_0
                CDHe4[0] = CDHe4_0
                summe[0] = summe_0
                for i in range(1, SimulationTime):
                    CD[i] = CD[i-1] + k10 * CDHe[i-1] * n_He * t - k01 * CD[i-1] * n_He * n_He * t
                    CDHe[i] = CDHe[i-1] + k01 * n_He * n_He * CD[i-1] * t - k10 * CDHe[i-1] * n_He * t + k21 * CDHe2[i-1] * n_He * t - k12 * CDHe[i-1] * n_He * n_He * t
                    CDHe2[i] = CDHe2[i-1] + k12 * n_He * n_He * CDHe[i-1] * t - k21 * CDHe2[i-1] * n_He * t + k32 * CDHe3[i-1] * n_He * t - k23 * CDHe2[i-1] * n_He * n_He * t
                    CDHe3[i] = CDHe3[i-1] + k23 * n_He * n_He * CDHe2[i-1] * t - k32 * CDHe3[i-1] * n_He * t + k43 * CDHe4[i-1] * n_He * t - k34 * CDHe3[i-1] * n_He * n_He * t
                    CDHe4[i] = CDHe4[i-1] + k34 * n_He * n_He * CDHe3[i-1] * t - k43 * CDHe4[i-1] * n_He * t
                    summe[i] = CD[i] + CDHe[i] + CDHe2[i] + CDHe3[i] + CDHe4[i]

                summe_meas = np.zeros(Timesteps)
                summe_meas = data[:, 1] + data[:, 2] + data[:, 3] + data[:, 4] + data[:, 5]

                plt.figure(1) #Initialisierung Plot1

                font = {'family' : 'arial',
                        'color'  : 'red',
                        'weight' : 'normal',
                        'size'   : 14,
                        }

                plt.plot(CD, 'r')
                plt.plot(data[:, 0], data[:, 1], 'ro')
                #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe, 'b')
                plt.plot(data[:, 0], data[:, 2], 'bo')
                #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe2, 'g')
                plt.plot(data[:, 0], data[:, 3], 'go')
                #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe3, 'm')
                plt.plot(data[:, 0], data[:, 4], 'mo')
                #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe4, 'y')
                plt.plot(data[:, 0], data[:, 5], 'yo')
                #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                plt.plot(summe, 'k')
                plt.plot(data[:, 0], summe_meas, 'ko')
                #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                plt.semilogy()
                plt.xlabel('reaction time [ms]')
                plt.ylabel('$He_n-CD^+$')
                plt.xlim([0, SimulationTime])
                plt.ylim([0.05, x_max])
                plt.show()
                Replot = input("Erneut plotten (y/n)? : ")
                if Replot == "y":
                    fitokay = 0
                    parameterfile = open(ParameterFilesInDir[int(FileNumber)], 'r')
                    parameter_lines = parameterfile.readlines()
                    parameters = []
                    parameterlist = {}

                    for i in parameter_lines:
                        parameters.append(i.strip().split())

                    for i in range(len(parameters)):
                        parameterlist[parameters[i][0]] = parameters[i][1]

                    for i in ListofParameters:
                        try:
                            locals()[i] = int(parameterlist[i])  # erzeugt Variablen mit den Namen in der oben definierten Liste
                        except KeyError:
                            print("Warning: " + i + " is not defined in the parameter file")  # Gibt eine Warnung aus, wenn die Variable nicht in der Parameterdatei vorhanden ist
                        except ValueError:
                            try:
                                locals()[i] = float(parameterlist[i])  # Wenn der Wert der Variablen kein Integer ist, versucht das Programm den Wert als Float einzulesen
                            except ValueError:
                                print("Error: parameter " + i + "has not the correct format")
                else:
                    fitokay = 1
                    Save = input("Moechten Sie den Plot speichern (y/n)? : ")
                    if Save == "y":
                        Name_parts = sys.path.basename(DataFilesInDir[int(FileNumber)]).split("_")
                        plot_name = Name_parts[0] + "_" + Name_parts[1]
                        plt.plot(CD, 'r')
                        plt.plot(data[:, 0], data[:, 1], 'ro')
                        #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe, 'b')
                        plt.plot(data[:, 0], data[:, 2], 'bo')
                        #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe2, 'g')
                        plt.plot(data[:, 0], data[:, 3], 'go')
                        #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe3, 'm')
                        plt.plot(data[:, 0], data[:, 4], 'mo')
                        #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe4, 'y')
                        plt.plot(data[:, 0], data[:, 5], 'yo')
                        #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(summe, 'k')
                        plt.plot(data[:, 0], summe_meas, 'ko')
                        #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                        plt.semilogy()
                        plt.xlabel('reaction time [ms]')
                        plt.ylabel('$He_n-CD^+$')
                        plt.xlim([0, SimulationTime])
                        plt.ylim([0.05, x_max])
                        plt.savefig(directory + "/" + plot_name + ".png", dpi=600)
                        if sys.path.isfile(directory + "/" + plot_name + ".png") == True:
                            print("Ihre Datei wurde unter " + directory + "/" + plot_name + ".png" + " abgespeichert.")
                        else:
                            print("Fehler beim schreiben der Datei")

        elif NumberOfMasses == 6:
            while fitokay == 0:
                CD_0 = data[StartTimeStep][NumberOfMasses + 1]
                CDHe_0 = 0
                CDHe2_0 = 0
                CDHe3_0 = 0
                CDHe4_0 = 0
                CDHe5_0 = 0
                summe_0 = CD_0 + CDHe_0 + CDHe2_0 + CDHe3_0 + CDHe4_0 + CDHe5_0
                CD = np.zeros(SimulationTime)
                CDHe = np.zeros(SimulationTime)
                CDHe2 = np.zeros(SimulationTime)
                CDHe3 = np.zeros(SimulationTime)
                CDHe4 = np.zeros(SimulationTime)
                CDHe5 = np.zeros(SimulationTime)
                summe = np.zeros(SimulationTime)
                CD[0] = CD_0
                CDHe[0] = CDHe_0
                CDHe2[0] = CDHe2_0
                CDHe3[0] = CDHe3_0
                CDHe4[0] = CDHe4_0
                CDHe5[0] = CDHe5_0
                summe[0] = summe_0
                for i in range(1, SimulationTime):
                    CD[i] = CD[i-1] + k10 * CDHe[i-1] * n_He * t - k01 * CD[i-1] * n_He * n_He * t
                    CDHe[i] = CDHe[i-1] + k01 * n_He * n_He * CD[i-1] * t - k10 * CDHe[i-1] * n_He * t + k21 * CDHe2[i-1] * n_He * t - k12 * CDHe[i-1] * n_He * n_He * t
                    CDHe2[i] = CDHe2[i-1] + k12 * n_He * n_He * CDHe[i-1] * t - k21 * CDHe2[i-1] * n_He * t + k32 * CDHe3[i-1] * n_He * t - k23 * CDHe2[i-1] * n_He * n_He * t
                    CDHe3[i] = CDHe3[i-1] + k23 * n_He * n_He * CDHe2[i-1] * t - k32 * CDHe3[i-1] * n_He * t + k43 * CDHe4[i-1] * n_He * t - k34 * CDHe3[i-1] * n_He * n_He * t
                    CDHe4[i] = CDHe4[i-1] + k34 * n_He * n_He * CDHe3[i-1] * t - k43 * CDHe4[i-1] * n_He * t + k54 * CDHe5[i-1] * n_He * t - k45 * CDHe4[i-1] * n_He * n_He * t
                    CDHe5[i] = CDHe5[i-1] + k45 * n_He * n_He * CDHe4[i-1] * t - k54 * CDHe5[i-1] * n_He * t
                    summe[i] = CD[i] + CDHe[i] + CDHe2[i] + CDHe3[i] + CDHe4[i] + CDHe5[i]

                summe_meas = np.zeros(Timesteps)
                summe_meas = data[:, 1] + data[:, 2] + data[:, 3] + data[:, 4] + data[:, 5] + data[:, 6]

                plt.figure(1) #Initialisierung Plot1

                font = {'family' : 'arial',
                        'color'  : 'red',
                        'weight' : 'normal',
                        'size'   : 14,
                        }

                plt.plot(CD, 'r')
                plt.plot(data[:, 0], data[:, 1], 'ro')
                #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe, 'b')
                plt.plot(data[:, 0], data[:, 2], 'bo')
                #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe2, 'g')
                plt.plot(data[:, 0], data[:, 3], 'go')
                #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe3, 'm')
                plt.plot(data[:, 0], data[:, 4], 'mo')
                #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe4, 'y')
                plt.plot(data[:, 0], data[:, 5], 'yo')
                #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                plt.plot(CDHe5, 'c')
                plt.plot(data[:, 0], data[:, 6], 'co')
                plt.plot(summe, 'k')
                plt.plot(data[:, 0], summe_meas, 'ko')
                #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                plt.semilogy()
                plt.xlabel('reaction time [ms]')
                plt.ylabel('$He_n-CD^+$')
                plt.xlim([0, SimulationTime])
                plt.ylim([0.05, x_max])
                plt.show()
                Replot = input("Erneut plotten (y/n)? : ")
                if Replot == "y":
                    fitokay = 0
                    parameterfile = open(ParameterFilesInDir[int(FileNumber)], 'r')
                    parameter_lines = parameterfile.readlines()
                    parameters = []
                    parameterlist = {}

                    for i in parameter_lines:
                        parameters.append(i.strip().split())

                    for i in range(len(parameters)):
                        parameterlist[parameters[i][0]] = parameters[i][1]

                    for i in ListofParameters:
                        try:
                            locals()[i] = int(parameterlist[i])  # erzeugt Variablen mit den Namen in der oben definierten Liste
                        except KeyError:
                            print("Warning: " + i + " is not defined in the parameter file")  # Gibt eine Warnung aus, wenn die Variable nicht in der Parameterdatei vorhanden ist
                        except ValueError:
                            try:
                                locals()[i] = float(parameterlist[i])  # Wenn der Wert der Variablen kein Integer ist, versucht das Programm den Wert als Float einzulesen
                            except ValueError:
                                print("Error: parameter " + i + "has not the correct format")
                else:
                    fitokay = 1
                    Save = input("Moechten Sie den Plot speichern (y/n)? : ")
                    if Save == "y":
                        Name_parts = sys.path.basename(DataFilesInDir[int(FileNumber)]).split("_")
                        plot_name = Name_parts[0] + "_" + Name_parts[1]
                        plt.plot(CD, 'r')
                        plt.plot(data[:, 0], data[:, 1], 'ro')
                        #plt.text(1600, 2500, '$CD^+$', {'color': 'r', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe, 'b')
                        plt.plot(data[:, 0], data[:, 2], 'bo')
                        #plt.text(1600, 1000, '$He-CD^+$', {'color': 'b', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe2, 'g')
                        plt.plot(data[:, 0], data[:, 3], 'go')
                        #plt.text(1600, 40, '$He_2-CD^+$', {'color': 'g', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe3, 'm')
                        plt.plot(data[:, 0], data[:, 4], 'mo')
                        #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe4, 'y')
                        plt.plot(data[:, 0], data[:, 5], 'yo')
                        #plt.text(1600, 6, '$He_3-CD^+$', {'color': 'm', 'fontsize': 12, 'family': 'arial'})
                        plt.plot(CDHe5, color='#1EA0E4')
                        plt.plot(data[:, 0], data[:, 6], color='"#1EA0E4"')
                        plt.plot(summe, 'k')
                        plt.plot(data[:, 0], summe_meas, 'ko')
                        #plt.text(1600, 2000, '$sum$', {'color': 'k', 'fontsize': 12, 'family': 'arial'})
                        plt.semilogy()
                        plt.xlabel('reaction time [ms]')
                        plt.ylabel('$He_n-CD^+$')
                        plt.xlim([0, SimulationTime])
                        plt.ylim([0.05, x_max])
                        plt.savefig(directory + "/" + plot_name + ".png", dpi=600)
                        if sys.path.isfile(directory + "/" + plot_name + ".png") == True:
                            print("Ihre Datei wurde unter " + directory + "/" + plot_name + ".png" + " abgespeichert.")
                        else:
                            print("Fehler beim schreiben der Datei")

    elif UserChoice == 0:
        print("Goodbye!")
        runprogram = 0