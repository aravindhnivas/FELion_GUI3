__author__ = 'kluge_admin'

import numpy as np
import matplotlib.pyplot as plt
from Class_Definitions import Fonts

F = Fonts()

# ## define constants

g_up = 3
g_low = 1
h = 6.626e-34
k_boltzmann = 1.38e-23
T = 5.7
nu = 453e9
a = 1

# ## calculate constants for simulation

c4 = g_up/g_low
c5 = np.exp(-h*nu/k_boltzmann/T)


# ## run simulation with different a


variable = np.arange(0, 1, 0.0001)
LIICG_signal = np.zeros(len(variable), dtype=float)
for i in range(len(variable)):
    a = variable[i]
    LIICG_signal[i] = (c4*(1-c5)*(1-a))/((1+c4)+a*(1+c4)*c4*c5)
plt.plot(variable, LIICG_signal, 'r')
plt.xlabel("a", fontdict=F.font2)
plt.ylabel("LIICG Signal in %", fontdict=F.font2)
plt.show()
LIICG_Meas = 30
diff = np.zeros(len(variable), dtype=float)
for i in range(len(variable)):
    diff[i] = abs(LIICG_Meas - LIICG_signal[i]*100)

min = min(diff)
for i in range(len(diff)):
    if diff[i] == min:
        print(i*0.0001)

a = (c4-c4*c5-LIICG_Meas/100-c4*LIICG_Meas/100)/(c4*c5*LIICG_Meas/100+c4*c4*c5*LIICG_Meas/100+c4-c4*c5)
print(a)