__author__ = 'Kluge'


import matplotlib as plt
import numpy as np
import pylab as py
from Class_Definitions import Fonts

F = Fonts()

def plot_density():
    file1 = "D:\Daten\SimDaten\_03112014\Dens\LIICG\LIICG_Variation_THzPower_a=0.6n_He=300000000000000.0.txt"
    file2 = "D:\Daten\SimDaten\_03112014\Dens\LIICG\LIICG_Variation_THzPower_a=0.6n_He=500000000000000.0.txt"
    #file3 = "D:\Daten\SimDaten\_07102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=50000000000000.0.txt"
    #file4 = "D:\Daten\SimDaten\_07102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=100000000000000.0.txt"
    #file5 = "D:\Daten\SimDaten\_07102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=500000000000000.0.txt"
    #file6 = "D:\Daten\SimDaten\_07102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=1000000000000000.0.txt"
    x1, y1 = np.loadtxt(file1, usecols=(0, 1), unpack=True)
    x2, y2 = np.loadtxt(file2, usecols=(0, 1), unpack=True)
    #x3, y3 = np.loadtxt(file3, usecols=(0, 1), unpack=True)
    #x4, y4 = np.loadtxt(file4, usecols=(0, 1), unpack=True)
    #x5, y5 = np.loadtxt(file5, usecols=(0, 1), unpack=True)
    #x6, y6 = np.loadtxt(file6, usecols=(0, 1), unpack=True)
    max_y1 = max(y1)
    max_y2 = max(y2)
    #max_y3 = max(y3)
    #max_y4 = max(y4)
    #max_y5 = max(y5)
    #max_y6 = max(y6)
    py.plot(x1*100, y1, color="#000000")  # black
    py.plot(x2*100, y2, color="#CD253B")  # red
    #py.plot(x3*100, y3, color="#0082C6")  # blue
    #py.plot(x4*100, y4, color="#1EA0E4")  # light blue
    #py.plot(x5*100, y5, color="#590F68")  # lila
    #py.plot(x6*100, y6, color="#772D86")  # light lila
    py.text(101, max_y1, "3e14", color="#000000")
    py.text(101, max_y2, "5e14", color="#CD253B")
    #py.text(101, max_y3, "5e13", color="#0082C6")
    #py.text(101, max_y4, "1e14", color="#1EA0E4")
    #py.text(101, max_y5, "5e14", color="#590F68")
    #py.text(101, max_y6, "1e15", color="#772D86")
    py.xlabel("THz Power in % (100% = 10µW)", fontdict=F.font2)
    py.ylabel("LIICG Signal in %", fontdict=F.font2)
    py.title("Simulation of LIICG-signal of CD+, a=0.6", fontdict=F.font1)
    py.show()

def plot_a():
    file1 = "D:\Daten\_19092014\LIICG_Variation_THzPower_a=0.0n_He=1000000000000000.0.txt"
    file2 = "D:\Daten\_19092014\LIICG_Variation_THzPower_a=0.2n_He=1000000000000000.0.txt"
    file3 = "D:\Daten\_19092014\LIICG_Variation_THzPower_a=0.4n_He=1000000000000000.0.txt"
    file4 = "D:\Daten\_19092014\LIICG_Variation_THzPower_a=0.5n_He=1000000000000000.0.txt"
    file5 = "D:\Daten\_19092014\LIICG_Variation_THzPower_a=0.6n_He=1000000000000000.0.txt"
    file6 = "D:\Daten\_19092014\LIICG_Variation_THzPower_a=0.8n_He=1000000000000000.0.txt"
    x1, y1 = np.loadtxt(file1, usecols=(0, 1), unpack=True)
    x2, y2 = np.loadtxt(file2, usecols=(0, 1), unpack=True)
    x3, y3 = np.loadtxt(file3, usecols=(0, 1), unpack=True)
    x4, y4 = np.loadtxt(file4, usecols=(0, 1), unpack=True)
    x5, y5 = np.loadtxt(file5, usecols=(0, 1), unpack=True)
    x6, y6 = np.loadtxt(file6, usecols=(0, 1), unpack=True)
    max_y1 = max(y1)
    max_y2 = max(y2)
    max_y3 = max(y3)
    max_y4 = max(y4)
    max_y5 = max(y5)
    max_y6 = max(y6)
    py.plot(x1*100, y1, color="#CD253B")  # red
    py.plot(x2*100, y2, color="#83AF23")  # green
    py.plot(x3*100, y3, color="#0082C6")  # blue
    py.plot(x4*100, y4, color="#1EA0E4")  # light blue
    py.plot(x5*100, y5, color="#590F68")  # lila
    py.plot(x6*100, y6, color="#772D86")  # light lila
    py.text(101, max_y1, "0.0", color="#CD253B")
    py.text(101, max_y2, "0.2", color="#83AF23")
    py.text(101, max_y3, "0.4", color="#0082C6")
    py.text(101, max_y4, "0.5", color="#1EA0E4")
    py.text(101, max_y5, "0.6", color="#590F68")
    py.text(101, max_y6, "0.8", color="#772D86")
    py.xlabel("THz Power in % (100% = 0.1µW)", fontdict=F.font2)
    py.ylabel("LIICG Signal in %", fontdict=F.font2)
    py.title("Simulation of LIICG-signal of CD+, n=1e15", fontdict=F.font1)
    py.show()

def plot_T():
    file1 = "D:\Daten\SimDaten\_07102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=500000000000000.0.txt"
    file2 = "D:\Daten\SimDaten\_08102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=500000000000000.0.txt"
    file3 = "D:\Daten\SimDaten\_09102014\LIICG\LIICG_Variation_THzPower_a=0.4n_He=500000000000000.0.txt"
    x1, y1 = np.loadtxt(file1, usecols=(0, 1), unpack=True)
    x2, y2 = np.loadtxt(file2, usecols=(0, 1), unpack=True)
    x3, y3 = np.loadtxt(file3, usecols=(0, 1), unpack=True)
    max_y1 = max(y1)
    max_y2 = max(y2)
    max_y3 = max(y3)
    py.plot(x1*100, y1, color="#CD253B")  # red
    py.plot(x2*100, y2, color="#83AF23")  # green
    py.plot(x3*100, y3, color="#0082C6")  # blue
    py.text(101, max_y1, "4K", color="#CD253B")
    py.text(101, max_y2, "7K", color="#83AF23")
    py.text(101, max_y3, "10K", color="#0082C6")
    py.xlabel("THz Power in % (100% = 0.1µW)", fontdict=F.font2)
    py.ylabel("LIICG Signal in %", fontdict=F.font2)
    py.title("Simulation of LIICG-signal of CD+, n=5e14", fontdict=F.font1)
    py.show()

def plot_LevelPop():
    y1 = []
    y2 = []
    y3 = []
    y4 = []
    y5 = []
    y6 = []
    file1 = open("D:\Daten\Dokumente\SimDaten\LevelPop\HCOLevelPopulation_on_THzPower=1e-05_a=0.5_n_He=250000000000000.0_TrapTime=600_Temp=5.3.txt", "r")
    length = 600000
    data = np.zeros((length, 6))
    for i in range(0, length):
            line = file1.readline()
            line = line.strip()
            data[i] = line.split()
    for i in range(len(data)):
        y1.append(data[i][0]/1000)
        y2.append(data[i][1]/1000)
        y3.append(data[i][2]/1000)
        y4.append(data[i][3]/1000)
        y5.append(data[i][4]/1000)
        y6.append(data[i][5]/1000)
    x_max = 600000
    y_max = 1
    pos_y1 = y1[x_max-1]
    pos_y2 = y2[x_max-1]
    pos_y3 = y3[x_max-1]
    pos_y4 = y4[x_max-1]
    pos_y5 = y5[x_max-1]
    py.plot(y1, color="#FF0000", label="HCO$^+$(0)")
    py.plot(y2, color="#83AF23", label="HCO$^+$(1)")
    py.plot(y3, color="#0082C6", label="HCO$^+$(2)")
    py.plot(y4, color="#590F68", label="HeHCO$^+$")
    py.plot(y5, color="#FF7F00", label="He$_2$HCO$^+$")
    py.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=5, mode="expand", borderaxespad=0., fontsize=12)
    py.xlim(0, x_max)
    py.ylim(0, y_max)
    x_ticks = [0]
    x_pos = [0]
    for i in range(5):
        #print(i)
        x_value = x_max/5
        x_pos.append(x_value*(i+1))
        x_ticks.append(x_value*(i+1)*0.0005)
    py.xticks(x_pos, x_ticks)
    py.xlabel("time [ms]", fontdict=F.font2)
    py.ylabel("amount of ions", fontdict=F.font2)
    path = "D:\Daten\Dokumente\SimDaten\_NewPlots\LevelPop_HCO+_on.png"
    py.savefig(path, format='png', dpi=600)
    py.show()
    #print(y1[3999999])
    #print(y2[3999999])
    #print(y3[3999999])
    #print(y4[3999999])
    #print(y5[3999999])


def plot_single():
    x = []
    y = []
    file = open("D:\Daten\SimDaten\_03122014\_5E14\LIICG\LIICG_Variation_TrapTime_a=0.6n_He=500000000000000.0.txt", "r")
    x1, y1 = np.loadtxt(file, usecols=(0, 1), unpack=True)
    #NumberOfLines = len(file.readlines())
    #print(NumberOfLines)
    #data = np.zeros((NumberOfLines, 2))
    #print(data)
    #for i in range(0, NumberOfLines):
    #    line = file.readline()
    #    line = line.strip()
    #    data[i] = line.split()

    py.title("Cluster Depletion Signal vs Storage Time, T=4K, n=1e15, a=0.6", fontdict=F.font1)
    py.plot(x1, y1, color="#CD253B", marker='o', linestyle="None")
    #py.axhline(linewidth=0.5, color='r')
    py.xlabel("storage time [ms]", fontdict=F.font2)
    py.ylabel("cluster depletion signal [%]", fontdict=F.font2)
    py.show()


#plot_density()
#plot_a()
#plot_T()
plot_LevelPop()
#plot_single()