
import sys, json
import numpy as np
import matplotlib.pyplot as plt
from scipy.constants import speed_of_light, Boltzmann, Planck
from functools import reduce
from scipy.integrate import solve_ivp

from pathlib import Path as pt
from ROSAA_func import distribution, boltzman_distribution, \
    stimulated_absorption, stimulated_emission,\
    voigt, lorrentz_fwhm, gauss_fwhm


def lineshape_normalise():
    freq = float(main_parameters["freq"])  # transition frequency in Hz

    # doppler line width

    massIon = float(lineshape_conditions["IonMass(amu)"])
    tempIon = float(lineshape_conditions["IonTemperature(K)"])
    sigma = gauss_fwhm(freq, massIon, tempIon)

    # power broadening
    dipoleMoment = float(power_broadening["dipoleMoment(D)"])
    power = float(power_broadening["power(W)"])

    cp = float(power_broadening["cp"])
    gamma = lorrentz_fwhm(dipoleMoment, power, cp)

    # normalised line shape factor
    LineShape = voigt(gamma, sigma)
    
    # transition rate due to influence of mm-wave 
    # normalisation factor

    trap_area = float(main_parameters["trap_area"])
    norm = (power/(trap_area*speed_of_light))*LineShape
    
    print(f"{massIon=}\n{tempIon=}\n{sigma=:.2e}\n{gamma=:.2e}\n{LineShape=:.2e}\n{norm=:.2e}\n", flush=True)

    return norm


def getCollisionalRate(collisional_rates):
    
    rates = {}
    
    for i in range(totallevel):
        for j in range(totallevel):
            if i != j & j>i:
                deexciteRateConstantKey = f"q_{j}{i}"
                exciteRateConstantKey = f"q_{i}{j}"
                
                if q_deexcitation_mode:
                    
                    _temp = collisional_rates[deexciteRateConstantKey]
                    rates[deexciteRateConstantKey] = _temp
                    rates[exciteRateConstantKey] = _temp * distribution(i, j, Energy, trapTemp)
                    
                else:

                    _temp = collisional_rates[exciteRateConstantKey]
                    rates[exciteRateConstantKey] = _temp
                    rates[deexciteRateConstantKey] = _temp * distribution(j, i, Energy, trapTemp)
    return rates

def getAttachmentRates():
    
    Rate_K3 = [float(i.strip())*nHe**2 for i in rate_coefficients["k3"].split(",")]

    a = float(rate_coefficients["a"])
    Rate_K3_excited = a*Rate_K3[0]
    Rate_kCID = [float(i.strip())*nHe for i in rate_coefficients["kCID"].split(",")]
    return Rate_K3, Rate_kCID, Rate_K3_excited


def computeAttachmentProcess(N, N_He, dR_dt):
    
    attachmentRate0 = - Rate_K3[0]*N[0] + Rate_kCID[0]*N_He[0]*p
    attachmentRate1 = - Rate_K3_excited*N[1] + Rate_kCID[0]*N_He[0]*(1-p)
    dR_dt[0] += attachmentRate0
    dR_dt[1] += attachmentRate1
    currentRate =  - attachmentRate0 - attachmentRate1

    for i in range(totalAttachmentLevels-1):
        nextRate = - Rate_K3[i+1]*N_He[i] + Rate_kCID[i+1]*N_He[i+1]
        attachmentRate = currentRate + nextRate
        currentRate = -nextRate
        dR_dt.append(attachmentRate)
        
    dR_dt.append(currentRate)
    if testMode: print(f"{dR_dt=}")
    return dR_dt

def computeCollisionalProcess(i, N):
    
    collections = []

    for j in range(totallevel):
        if i!= j: 
            
            key = f"q_{j}{i}"
            keyInverse = f"q_{i}{j}"
            
            k = collisional_rates[key]*nHe*N[j] - collisional_rates[keyInverse]*nHe*N[i]
            collections.append(k)
    
    if testMode: print(f"collisional_collection: \t{collections}")
    return collections

def computeEinsteinProcess(i, N):
    collections = []
    
    if includeSpontaneousEmission:

        # Einstein Coefficient A
        if i == excitedFrom: 
            temp = A_10*N[excitedTo]
            collections.append(temp)

        if i == excitedTo:
            temp = -A_10*N[excitedTo]
            collections.append(temp)

    # Einstein Coefficient B
    if lightON:
        
        # B_rate defined from excited state 
        B_rate = B_01*N[excitedFrom] - B_10*N[excitedTo]

        if i==excitedFrom:
            temp = -B_rate
            collections.append(temp)

        if i==excitedTo:
            temp = B_rate
            collections.append(temp)
    if testMode: print(f"einstein_collection: \t{collections}")
    return collections

def computeRateDistributionEquations(t, counts):
    if includeAttachmentRate:
        N =  counts[:-totalAttachmentLevels]
        N_He = counts[-totalAttachmentLevels:]

    else:
        N = counts
    
    rateCollection = []
    
    for i in range(totallevel):
        if testMode: print(f"\n\nLevel {i=}\n\n")
        collisional_collection = computeCollisionalProcess(i, N)
        einstein_collection = computeEinsteinProcess(i, N)
        collections = collisional_collection + einstein_collection
        rateCollection.append(collections)
        if testMode: print(f"{rateCollection=}")
        
    dR_dt = []
    for _ in rateCollection:
        _temp = reduce(lambda a, b: a+b, _)
        dR_dt.append(_temp)
        
    if includeAttachmentRate:
        dR_dt = computeAttachmentProcess(N, N_He, dR_dt)
    return dR_dt

def sendData(currentLocation, filename, dataToSend):
    with open(pt(currentLocation) / f"{filename}.json", 'w+') as f:

        data = json.dumps(dataToSend, sort_keys=True, indent=4, separators=(',', ': '))
        f.write(data)

if __name__ == "__main__":

    args = sys.argv[1:][0].split(",")
    args = json.loads(", ".join(args))
    conditions = args
    
    writefile, filename, currentLocation = args["writefile"], args["filename"], args["currentLocation"]
    sendData(currentLocation, filename, args)
    logFile = open(pt(currentLocation) / f"{filename}_logFile.txt", 'w+')
    
    main_parameters = conditions["main_parameters"]
    simulation_parameters = conditions["simulation_parameters"]
    einstein_coefficient = conditions["einstein_coefficient"]
    lineshape_conditions = conditions["lineshape_conditions"]
    rate_coefficients = conditions["rate_coefficients"]
    power_broadening = conditions["power_broadening"]

    variable, variableRange = conditions["variable"], conditions["variableRange"]
    nHe = float(rate_coefficients["He density(cm3)"])
    print(f"{nHe=:.2e}\n", flush=True)

    Rate_K3, Rate_kCID, Rate_K3_excited = getAttachmentRates()

    p = float(rate_coefficients["branching-ratio"])
    print(f"Branching Ratio: {p}\n")

    includeSpontaneousEmission = conditions["includeSpontaneousEmission"]
    includeCollision = conditions["includeCollision"]
    includeAttachmentRate = conditions["includeAttachmentRate"]
    
    print(f"{includeAttachmentRate=}\n{includeCollision=}\n{includeSpontaneousEmission=}\n", flush=True)

    totallevel = int(conditions["numberOfLevels"])
    print(f"{totallevel=}\n", flush=True)

    Energy = [float(_) for _ in main_parameters["Energy"].split(", ")]
    trapTemp = float(conditions["trapTemp"])
    print(f"{Energy=} in cm-1\n{trapTemp=}K", flush=True)

    excitedTo = simulation_parameters["excitedTo"]
    excitedFrom = simulation_parameters["excitedFrom"]

    freq = float(main_parameters["freq"])  # transition frequency in Hz
    print(f"{freq=:.4e} Hz\n", flush=True)

    norm = lineshape_normalise()
    A_10 = float(einstein_coefficient["A_10"])
    print(f"{A_10=:.2e}\n", flush=True)

    B_10 = stimulated_emission(A_10, freq)*norm
    B_01 = stimulated_absorption(excitedFrom, excitedTo, B_10)
    print(f"{B_10=:.2e}\t{B_01=:.2e}\n", flush=True)

    collisional_rates = {q:float(value) for q, value in conditions["collisional_rates"].items()}
    q_deexcitation_mode = conditions["deexcitation"]
    collisional_rates = getCollisionalRate(collisional_rates)

    print(f"Collisional Rates", flush=True)
    for key, value in collisional_rates.items():
        print(f"{key}: {value:.2e}\t{key}*nHe: {value*nHe:.2e}\n", flush=True)
    
    simulation_time = int(simulation_parameters["Simulation time(ms)"])*1e-3
    tspan = [0, simulation_time]
    totalAttachmentLevels = int(rate_coefficients["totalAttachmentLevels"])
    N = boltzman_distribution(Energy, 300)[:totallevel]
    N_He = totalAttachmentLevels*[0]

    boltzman_distribution_source = (N, [*N, *N_He])[includeAttachmentRate]
    print(f"{boltzman_distribution_source=}", flush=True)
    
    totalSteps = int(simulation_parameters["Total steps"])

    simulateTime = np.linspace(0, simulation_time, totalSteps)
    simulateTime_ms = simulateTime*1e3

    testMode = False
    print(f"LightOFF", flush=True)

    lightON=False
    Noff = solve_ivp(computeRateDistributionEquations, tspan, boltzman_distribution_source, dense_output=True)
    
    resOffCounts = Noff.sol(simulateTime)
    print(f"boltzman population after trapping (Res OFF): {resOffCounts.T[-1]}", flush=True)

    molecule = main_parameters["molecule"]
    taggingPartner = main_parameters["tagging partner"]

    if includeAttachmentRate and includeSpontaneousEmission:
        print(f"LightON", flush=True)
        lightON=True
        Non = solve_ivp(computeRateDistributionEquations, tspan, boltzman_distribution_source, dense_output=True)
        
        resOnCounts = Non.sol(simulateTime)

        fig, (ax, ax1) = plt.subplots(ncols=2, figsize=(12, 4), dpi=100)
        
        legends = [f"{molecule}{i}" for i in range(totallevel)]
        if includeAttachmentRate:
            legends += [f"{molecule}He"]
            legends += [f"{molecule}{taggingPartner}{i+1}" for i in range(1, totalAttachmentLevels)]

        counter = 0
        for on, off in zip(resOnCounts, resOffCounts):

            ax.plot(simulateTime_ms, on, f"-C{counter}", label=legends[counter])
            ax.plot(simulateTime_ms, off, f"--C{counter}")
            counter += 1
            
        ax.plot(simulateTime_ms, resOnCounts.sum(axis=0), "k")

        ax.legend(title=f"-ON, --OFF")
        ax.set(yscale="log", ylabel="Counts", xlabel="Time(ms)")
        ax.minorticks_on()

        signal = (1 - (resOnCounts[-2][1:] / resOffCounts[-2][1:]))*100
        ax1.plot(simulateTime_ms[1:], signal)
        ax1.legend([f"Max. Signal = {signal.max():.2f} at {(simulateTime_ms[1:][signal.argmax()]):.2f}ms"])
        ax1.minorticks_on()
        ax1.set(title="Signal as a function of trap time", xlabel="Time (ms)", ylabel="Signal (%)")
        plt.tight_layout()
        plt.show()
        print(f"Signal: {(1 - (resOnCounts[-2][-1] / resOffCounts[-2][-1]))*100:.2f}%", flush=True)
    
    else:
        fig, ax = plt.subplots(figsize=(7, 5), dpi=100)
        legends = [f"{molecule}{i}" for i in range(totallevel)]
        ax.plot(simulateTime_ms.T, resOffCounts.T)
        ax.plot(simulateTime_ms, resOffCounts.sum(axis=0), "k")
        ax.legend(legends, title=f"Collisional Cooling")
        ax.set(ylabel="Counts", xlabel="Time(ms)", title=f"Simulation: Thermal stabilisation by collision with {taggingPartner} atoms (300=>{trapTemp})K")

        ax.minorticks_on()
        plt.tight_layout()
        plt.show()


    logFile.close()