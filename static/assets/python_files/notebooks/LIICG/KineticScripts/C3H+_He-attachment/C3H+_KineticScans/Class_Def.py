__author__ = 'Kluge'


import numpy as np


class Ions:
    def __init__(self):
        self.CD_0_on = np.zeros(1)
        self.CD_1_on = np.zeros(1)
        self.CD_2_on = np.zeros(1)
        self.CDHe_on = np.zeros(1)
        self.CDHe2_on = np.zeros(1)
        self.sum_on = np.zeros(1)

        self.CD_0_off = np.zeros(1)
        self.CD_1_off = np.zeros(1)
        self.CD_2_off = np.zeros(1)
        self.CDHe_off = np.zeros(1)
        self.CDHe2_off = np.zeros(1)
        self.sum_off = np.zeros(1)
        self.LIICG = 0.0

        self.N0 = 0.0
        self.N1 = 0.0
        self.N2 = 0.0


class Conditions:
    def __init__(self):
        self.temp = 0.0
        self.n_He = 1e14
        self.P_THz = 1e-6
        self.p = 0.5
        self.time = 100
        self.A_trap = 5e-5
        self.alpha = 1e5


class Ratecoefficients:
    def __init__(self):
        self.k3_0 = 3e-30
        self.k3_1 = 1.5e-30
        self.k32 = 6e-30
        self.kCID = 2e-15
        self.kCID2 = 4e-15

        self.q_01 = 0.0
        self.q_10 = 0.0
        self.q_12 = 0.0
        self.q_21 = 0.0
        self.q_02 = 0.0
        self.q_20 = 0.0

        self.A_10 = 0.0
        self.B_10 = 0.0
        self.B_01 =0.0



class Rates:
    def __init__(self):
        self.Rate_B_01 = 0.0
        self.Rate_B_10 = 0.0
        self.Rate_A_10 = 0.0
        self.Rate_k3_0 = 0.0
        self.Rate_k3_1 = 0.0
        self.Rate_k32 = 0.0
        self.Rate_K_CID = 0.0
        self.Rate_K_CID2 = 0.0
        self.Rate_q_01 = 0.0
        self.Rate_q_10 = 0.0
        self.Rate_q_12 = 0.0
        self.Rate_q_21 = 0.0
        self.Rate_q_02 = 0.0
        self.Rate_q_20 = 0.0


class Time:
    def __init__(self):
        self.step = 0.0
        self.timestep = 0.0
        self.num_steps = 0.0


class Fonts:
    def __init__(self):
        self.font1 = {'family': 'serif', 'color': 'darkred', 'weight': 'normal', 'size': 14}
        self.font2 = {'family': 'serif','color': 'black', 'weight': 'normal', 'size': 18}