# -*- coding: utf-8 -*-
import os
import numpy as np
import matplotlib.pyplot as plt
import math

# Open measurement file
file = 'C:/Python27/Programs/C3H+_He-attachment/20131210_140925_timescan.txt'
f = open(file, 'r')

savedir = os.path.dirname(file)
filename = os.path.basename(file)
savename = filename.split('.')[0]

print(savename)


# Define some parameters
nts = 19 # Number of time steps in measurement
nm = 5 # Number of masses to plot
nc = nm + 1 # Number of columns including time

filename = os.path.basename(file)

#Bedingungen Messung
T_Trap = 4.0            #Temperatur der Falle in K
t = 0.001               #Zeitintervall in s
T = 1000                 #Zeit in ms

# Calculate He number density from pressure at 290K (Gerlich1992)
He_0 = 3.97e14
H2_0 = 8.0e-8 * He_0 # from earlier measurements
print (He_0)

# Remove header files (change to automatic header detect)
for i in range(1,10):
    test = f.readline()
    print(test)
    
# Initialize data array (first index number of time points
# Second index masses plus time plus sum (automatize)
data = np.zeros((nts,nc))

# read in lines after header and add to array
for i in range (0,nts):
    line = f.readline()
    line = line.strip()
    line
    data[i]=line.split()
#    print data[i]




C3H_0 = data[0,1]
HC3H_0 = data[0,2]
H2C3H_0 = data[0,3]
C3HHe_0 = data[0,4]


# print (H2HCO_0)


summe_0 = C3H_0 + HC3H_0 + H2C3H_0 + C3HHe_0



# Estimate kcid
## kcid =  math.exp(-300/20) * 10**(-9)
## print (kcid)

#Ratenkoeffizienten (guess)

k01= 4.8e-31 #k01 etc. tern�r cm6/s; CO+ + 2*He --> COHe+ + He, etc.
k12= 3.1e-30 # 
#k23= 4.8e-30
#k34= 0.0e-30
#k45= 0.0e-31
#k56= 3.5e-31
k10= 3.0e-14     #k10 etc. bin�re Fragmentierung cm�/s; COHe+ + He --> CO+ + 2*He
k21= 1.7e-14 
#k32= 1.0e-14  
#k43= 0.0e-15
#k10_2=2.4e-12 
#k54= 5.0e-15 
#k65= 5.0e-16 
kH2_1 = 5.0e-11    # binary C3H2+, Gerlich @ 10K: 5e-11
kH2_2 = 2.0e-10  # radiative C3H3+, Gerlich @ 10K: 2e-10

#Initialisiere Arrays

C3H = np.zeros(T)
HC3H = np.zeros(T)
H2C3H = np.zeros(T)
C3HHe = np.zeros(T)
summe = np.zeros(T)


C3H[0] = C3H_0
HC3H[0] = HC3H_0
H2C3H[0] = H2C3H_0
C3HHe[0] = C3HHe_0 


summe[0] = summe_0

for i in range(1,T):
    C3H[i]    = C3H[i-1]    - kH2_1 * H2_0 * C3H[i-1] *t          - kH2_2 * H2_0 * C3H[i-1] * t             + k10 * C3HHe[i-1]  * He_0 * t - k01 * C3H[i-1]    * He_0 * He_0 * t
    C3HHe[i]  = C3HHe[i-1]                                                                                  + k01 * He_0 * He_0 * C3H[i-1] * t - k10 * C3HHe[i-1]  * He_0 * t            
    HC3H[i]   = HC3H[i-1]   + kH2_1 * H2_0 * C3H[i-1] * t         
    H2C3H[i] =  H2C3H[i-1]  + kH2_2 * H2_0 * C3H[i-1] * t       
#    res[i] = k56 * COHe5[i-1]*He_0*He_0*t
    summe[i] = C3H[i] + C3HHe[i] + HC3H[i] + H2C3H[i]
#    test[i] = test [i-1] + k01 * He_0 * He_0 * CO[i-1]    * t
    
summe_meas = np.zeros(nts)
summe_meas = data[ : ,1]  + data[ : ,2] + data[ : ,3] + data[ : ,4] 



#Plotten der Simulierten Timescans
#Plotten der Messungen, setze Nullpunkt bei 10ms

plt.figure(1) #Initialisierung Plot1

font = {'family' : 'arial',
        'color'  : 'red',
        'weight' : 'normal',
        'size'   : 14,
        }
 
plt.plot(C3H,'r')
plt.plot(data[ : ,0]-10,data[ : ,1], 'ro')
plt.text(750, 2200, '$C_3H^+$', {'color' : 'r', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(C3HHe,'b')
plt.plot(data[ : ,0]-10,data[ : ,4], 'bo')
plt.text(750, 1000, '$He-C_3H^+$', {'color' : 'b', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(HC3H,'g')
plt.plot(data[ : ,0]-10,data[ : ,2], 'go')
plt.text(750, 5, '$C_3H_2^+$', {'color' : 'g', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(H2C3H,'m')
plt.plot(data[ : ,0]-10,data[ : ,3], 'mo')
plt.text(750, 30, '$C_3H_3^+$', {'color' : 'm', 'fontsize' : 12, 'family' : 'arial'})
#plt.plot(HCOHe4,'y')
#plt.plot(data[ : ,0]-10,data[ : ,6], 'yo')
#plt.text(400, 10, '$He_4-HCO^+$', {'color' : 'y', 'fontsize' : 12, 'family' : 'arial'})
#plt.plot(H2HCO, 'c')
#plt.plot(data[ : ,0]-20,data[ : ,2], 'co')
#plt.text(1350, 150, '$H2-HCO^+$', {'color' : 'c', 'fontsize' : 12, 'family' : 'arial'})
plt.plot(summe,'k')
plt.plot(data[ : ,0]-10,summe_meas, 'ko')
plt.text(750, 1800, '$sum$', {'color' : 'k', 'fontsize' : 12, 'family' : 'arial'})
#plt.plot(COHe6,'r')
#plt.plot(data[ : ,0]-100,data[ : ,7], 'ro')
#plt.plot(data[ : ,0]-100,data[ : ,7], 'co')
#plt.text(500,0.15, "k01=%f" %(k01))
plt.text(200,0.2, 'k01= %.2e' %(k01), {'color' : 'k', 'fontsize':10, 'family': 'arial'})
plt.text(200,0.15, 'k10= %.2e, k_H2_1=%.2e, k_H2_2=%.2e' %(k10, kH2_1, kH2_2), {'color' : 'k', 'fontsize':10, 'family': 'arial'})
plt.text(200,0.3, 'nHe=%.2e, T=%.1fK' %(He_0, T_Trap ), {'color' : 'k', 'fontsize':10, 'family': 'arial'})



plt.semilogy()

plt.title('%s fit with extended model' %(filename))

plt.xlabel('reaction time -10 [ms]')

plt.ylabel('N $He-HCO_n^+$')

plt.xlim([0,T])
plt.ylim([0.05, 15000])

savefile='%s/%s_%sKvalues_extModel.png'%(savedir, savename, T_Trap)
print(savefile)
plt.savefig(savefile)
plt.show()
