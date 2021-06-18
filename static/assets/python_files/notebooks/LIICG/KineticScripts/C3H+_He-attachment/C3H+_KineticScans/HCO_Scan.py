__author__ = 'Monika'
# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
from Class_Def import Fonts

F = Fonts()

# Open measurement file
file = 'D:/Daten/HCO/20131112_155538_timescan.txt'
f = open(file, 'r')
# Only first 400ms to get k3's better

# Define some parameters
nts = 30 # Number of time steps in measurement
nm = 6 # Number of masses to plot
nc = nm + 1 # Number of columns including time

filename = os.path.basename(file)

#Bedingungen Messung
T_Trap = 4            #Temperatur der Falle in K
t = 0.001               #Zeitintervall in s
T = 2000                 #Zeit in ms

# Calculate He number density from pressure at 290K (Gerlich1992)
He_0 = 4.13e14
H2_0 = 1.0e-4 * He_0 # from earlier measurements
print (He_0)

# Remove header files (change to automatic header detect)
for i in range(1,11):
    test = f.readline()
#    print(test)

# Initialize data array (first index number of time points
# Second index masses plus time plus sum (automatize)
data = np.zeros((nts,nc))

# read in lines after header and add to array
for i in range (0,nts):
    line = f.readline()
    line = line.strip()
    data[i]=line.split()
#    print data[i]




HCO_0 = data[2,1]
H2HCO_0 = data[0,2]
HCOHe_0 = data[0,3]
HCOHe2_0 = data[0,4]
HCOHe3_0 = data[0,5]
HCOHe4_0 = 0
#COHe5_0 = data[0,6]
#COHe6_0 = data[0,7]
#COHe7_0 = data[0,8]

print (H2HCO_0)


summe_0 = HCO_0 + HCOHe_0 + HCOHe2_0 + H2HCO_0 + HCOHe3_0



# Estimate kcid
## kcid =  math.exp(-300/20) * 10**(-9)
## print (kcid)

#Ratenkoeffizienten (guess)

k01= 1.65e-30 #k01 etc. tern�r cm6/s; CO+ + 2*He --> COHe+ + He, etc.
k12= 3.05e-30 #
k23= 6.0e-30
k34= 0.0e-30
#k45= 0.0e-31
#k56= 3.5e-31
k10= 3.3e-15     #k10 etc. bin�re Fragmentierung cm�/s; COHe+ + He --> CO+ + 2*He
k21= 9.0e-15
k32= 1.4e-14
k43= 0.0e-15
k10_2=1.4e-12
#k54= 5.0e-15
#k65= 5.0e-16
kH2 = 2.1e-14    # Mass 31 H2-HCO+ ternary
kH2CID = 0.0e-14  # Mass 31 dissociation binary

#Initialisiere Arrays

HCO = np.zeros(T)
HCOHe = np.zeros(T)
HCOHe2 = np.zeros(T)
HCOHe3 = np.zeros(T)
HCOHe4 = np.zeros(T)
H2HCO = np.zeros(T)
summe = np.zeros(T)


HCO[0] = HCO_0
HCOHe[0] = HCOHe_0
HCOHe2[0] = HCOHe2_0
HCOHe3[0] = HCOHe3_0
HCOHe4[0] = HCOHe4_0
H2HCO[0] = H2HCO_0

summe[0] = summe_0

for i in range(1,T):
    HCO[i]    = HCO[i-1]    - kH2 * H2_0 * HCO[i-1] *t + kH2CID * He_0 * H2HCO[i-1] * t                     + k10 * HCOHe[i-1]  * He_0 * t - k01 * HCO[i-1]    * He_0 * He_0 * t
    HCOHe[i]  = HCOHe[i-1]  + k01 * He_0 * He_0 * HCO[i-1]    * t - k10 * HCOHe[i-1]  * He_0 * t            + k21 * HCOHe2[i-1] * He_0 * t - k12 * HCOHe[i-1]  * He_0 * He_0 * t - k10_2 * HCOHe[i-1] * H2_0 * t
    HCOHe2[i] = HCOHe2[i-1] + k12 * He_0 * He_0 * HCOHe[i-1]  * t - k21 * HCOHe2[i-1] * He_0 * t            + k32 * HCOHe3[i-1] * He_0 * t - k23 * HCOHe2[i-1] * He_0 * He_0 * t
    HCOHe3[i] = HCOHe3[i-1] + k23 * He_0 * He_0 * HCOHe2[i-1] * t - k32 * HCOHe3[i-1] * He_0 * t            + k43 * HCOHe4[i-1] * He_0 * t - k34 * HCOHe3[i-1] * He_0 * He_0 * t
    HCOHe4[i] = HCOHe4[i-1] + k34 * He_0 * He_0 * HCOHe3[i-1] * t - k43 * HCOHe4[i-1] * He_0 * t
    H2HCO[i] =  H2HCO[i-1]  + kH2 * H2_0 * HCO[i-1] * t - kH2CID * He_0 * H2HCO[i-1] *t                                                                                          + k10_2 * HCOHe[i-1] * H2_0 * t
#    COHe6[i] = COHe6[i-1] + k56 * He_0 * He_0 * COHe5[i-1] * t - k65 * COHe6[i-1] * He_0 * t
#    res[i] = k56 * COHe5[i-1]*He_0*He_0*t
    summe[i] = HCO[i] + HCOHe[i] + HCOHe2[i] + HCOHe3[i] + H2HCO[i] + HCOHe4[i]
#    test[i] = test [i-1] + k01 * He_0 * He_0 * CO[i-1]    * t

summe_meas = np.zeros(nts)
summe_meas = data[ : ,1]  + data[ : ,2] + data[ : ,3] + data[ : ,4] + data[ : ,5]

print (HCO[T-1]/HCOHe[T-1])
print (HCOHe[T-1]/HCOHe2[T-1])


#Plotten der Simulierten Timescans
#Plotten der Messungen, setze Nullpunkt bei 10ms

plt.figure(1) #Initialisierung Plot1

font = {'family' : 'arial',
        'color'  : 'red',
        'weight' : 'normal',
        'size'   : 14,
        }

plt.plot(HCO,'r')
plt.plot(data[ : ,0]-10,data[ : ,1], 'ro')
#plt.text(1600, 2200, '$HCO^+$', {'color' : 'r', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(HCOHe,'b')
plt.plot(data[ : ,0]-10,data[ : ,3], 'bo')
#plt.text(1600, 1000, '$He-HCO^+$', {'color' : 'b', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(HCOHe2,'g')
plt.plot(data[ : ,0]-10,data[ : ,4], 'go')
#plt.text(1600, 180, '$He_2-HCO^+$', {'color' : 'g', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(HCOHe3,'m')
plt.plot(data[ : ,0]-10,data[ : ,5], 'mo')
#plt.text(1600, 7, '$He_3-HCO^+$', {'color' : 'm', 'fontsize' : 12, 'family' : 'arial'})
#plt.plot(HCOHe4,'y')
#plt.plot(data[ : ,0]-10,data[ : ,6], 'yo')
#plt.text(400, 10, '$He_4-HCO^+$', {'color' : 'y', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(H2HCO, 'c')
plt.plot(data[ : ,0]-10,data[ : ,2], 'co')
#plt.text(1600, 30, '$H2-HCO^+$', {'color' : 'c', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(summe,'k')
plt.plot(data[ : ,0]-10,summe_meas, 'ko')
#plt.text(1600, 1800, '$sum$', {'color' : 'k', 'fontsize' : 12, 'family' : 'arial'})
#plt.plot(COHe6,'r')
#plt.plot(data[ : ,0]-100,data[ : ,7], 'ro')
#plt.plot(data[ : ,0]-100,data[ : ,7], 'co')
#plt.text(500,0.15, "k01=%f" %(k01))
#plt.text(500,0.25, 'k01= %.2e, k12= %.2e, k23= %.2e' %(k01, k12, k23), {'color' : 'k', 'fontsize':10, 'family': 'arial'})
#plt.text(500,0.15, 'k10= %.2e, k21= %.2e, k32=%.2e, k10_2=%.2e, k_H2=%.2e' %(k10, k21, k32, k10_2, kH2), {'color' : 'k', 'fontsize':10, 'family': 'arial'})
#plt.text(500,0.08, 'nHe=%.2e, T=%.1fK' %(He_0, T_Trap ), {'color' : 'k', 'fontsize':10, 'family': 'arial'})



plt.semilogy()

#plt.title('%s fit with extended model' %(filename))

plt.xticks(fontsize = 16)
plt.yticks(fontsize = 16)
plt.xlabel("storage time [ms]", fontdict=F.font2)
plt.ylabel("number of ions", fontdict=F.font2)

plt.xlim([0,T])
plt.ylim([0.05, 10000])

plt.savefig('D:/Daten/HCO/TimeScan.png', format='png', dpi=400)
plt.show()
