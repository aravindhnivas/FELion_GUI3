from io import StringIO 
from numpy import (
    diff, append, copy, 
    genfromtxt, array, take,
    arange, log, digitize, zeros
)

from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from json import loads, dumps

def felix_read_file(felixfile, felixfileName):

    # data format --> undulatorWn, setWn, counts, sa
    file = genfromtxt(StringIO(felixfile))
    if ".felix" in felixfileName: data = file[:,0], file[:,2], file[:, 3] 
    elif ".cfelix" in felixfileName: data = file[:,0], file[:,1], file[:, 2]
    return take(data, data[0].argsort(), 1)

def inten_per_photon(wn, inten): return (array(wn) * array(inten)) / 1e3

def norm_line_felix(dataContents, felixfileName, nshots, PD=True):

    felixfileData, basefileData, powerfileData = dataContents
    data = felix_read_file(felixfileData, felixfileName)
    undulatorWn, counts, saWn = data
    # Calib wn
    
    linearfitfunc = lambda x, m, c: (m * x) + c
    calib_pop, _ = curve_fit(linearfitfunc, undulatorWn, saWn, p0=[1, 5] )
    calibWavelength = linearfitfunc(undulatorWn, *calib_pop)


    saX_wn = arange(undulatorWn.min(), undulatorWn.max(), 1)
    saY_fit_wn = linearfitfunc(saX_wn, *calib_pop)
    # linear-extrapolate power

    powData = genfromtxt(StringIO(powerfileData)).T
    powExtapolateFunc = interp1d(powData[0], powData[1], kind="linear", fill_value='extrapolate')
    
    measuredPower = powExtapolateFunc(undulatorWn)
    total_power = measuredPower*nshots

    # cubic-extrapolate baseline --> counts

    baseData = genfromtxt(StringIO(basefileData)).T
    baseData = take(baseData, baseData[0].argsort(), 1)
    baseExtapolateFunc = interp1d(baseData[0], baseData[1], kind="cubic")
    baseCounts = baseExtapolateFunc(undulatorWn)

    # Normalise the intensity
    # multiply by 1000 because of mJ but ONLY FOR PD!!!
    ratio = counts/baseCounts
    if PD:
        intensity = (-log(ratio)/total_power)*1000
    else:
        intensity = (baseCounts-counts)/total_power
        
    relative_depletion =(1-ratio)*100
    return calibWavelength, intensity, counts, relative_depletion,\
        total_power, undulatorWn, saWn, saX_wn, saY_fit_wn, baseData

def felix_binning(xs, ys, delta):

    """
    Binns the data provided in xs and ys to bins of width delta
    output: binns, intensity 
    """

    # bins = arange(start, end, delta)
    # occurance = zeros(start, end, delta)
    BIN_STEP = delta
    BIN_START = xs.min()
    BIN_STOP = xs.max()

    indices = xs.argsort()
    datax = xs[indices]
    datay = ys[indices]

    # print("In total we have: ", len(datax), ' data points.')
    # do the binning of the data
    bins = arange(BIN_START, BIN_STOP, BIN_STEP)
    # print("Binning starts: ", BIN_START,
    #    ' with step: ', BIN_STEP, ' ENDS: ', BIN_STOP)

    bin_i = digitize(datax, bins)
    bin_a = zeros(len(bins) + 1)
    bin_occ = zeros(len(bins) + 1)

    for i in range(datay.size):
        bin_a[bin_i[i]] += datay[i]
        bin_occ[bin_i[i]] += 1

    binsx, data_binned = [], []
    for i in range(bin_occ.size - 1):
        if bin_occ[i] > 0:
            binsx.append(bins[i] - BIN_STEP / 2)
            data_binned.append(bin_a[i] / bin_occ[i])

    # non_zero_i = bin_occ > 0
    # binsx = bins[non_zero_i] - BIN_STEP/2
    # data_binned = bin_a[non_zero_i]/bin_occ[non_zero_i]

    return binsx, data_binned

def makeDataToSend(x, y, name, update={}):

    return { **update, "x": list(x), "y": list(y), "name": name}

def normplot(received_files=[], delta=1):
    print("Starting")
    # print(f"{received_files=}", flush=True)
    received_files = loads(received_files)

    # print(f"{received_files[0]=}", flush=True)
    # return ""
    dataToSend = {"base": {}, "SA": {}, "pow": {}, "average": {}, "average_rel": {}, "average_per_photon": {}}

    # For Average binning (Norm. method: log)
    xs = array([], dtype=float)
    ys = array([], dtype=float)
    xs_r = array([], dtype=float)
    ys_r = array([], dtype=float)
    

    counter = 0
    for mainData in received_files:
        color = mainData["color"]
        filename = mainData["filename"] # without extension

        felixfile = mainData["felixfile"]
        basefile = mainData["basefile"]
        powerfile = mainData["powerfile"]
        felix_hz = felixfile["felix_hz"]
        nshots = felixfile["nshots"]
        dataContents = [felixfile['data'], basefile['data'], powerfile['data']]



        felixfileName = str(felixfile['name'])

        # Wavelength and intensity of individuals without binning
        
        wavelength, intensity, counts, \
        relative_depletion, total_power,\
        undulatorWn, saWn, saX_wn, saY_fit_wn, baseData \
             = norm_line_felix(dataContents, felixfileName, nshots)
        
        # print(f"{data[0].tolist()=}")
             
        # calibWavelength, intensity, counts, relative_depletion,\
        # total_power, data, saX_wn, saY_fit_wn, baseData
        wavelength_rel = copy(wavelength)

        # collecting Wavelength and intensity to average spectrum with binning

        xs = append(xs, wavelength)
        ys = append(ys, intensity)

        xs_r = append(xs_r, wavelength_rel)
        ys_r = append(ys_r, relative_depletion)
        
        energyJ = inten_per_photon(wavelength, intensity)

        ################### Spectrum Analyser #################################
        lineColor = {"color": f"rgb{color}", "shape":"hv"}
        blackColor = {"color": "black"}
        groupItem = {"legendgroup": f'group{counter}'}
        nolegend = {"showlegend": False}
        
        dataToSend["SA"][felixfileName] = makeDataToSend(
            undulatorWn, saWn, f"{filename}_SA", 
            update={"line":lineColor, **groupItem, "mode": "markers"}
        )
        dataToSend["SA"][f"{felixfileName}_fit"] = makeDataToSend(
            saX_wn, saY_fit_wn, f"{filename}_fit", 
            update={"mode": "lines", "line": blackColor, **groupItem, **nolegend}
        )

        powlegend = f"{powerfile['name']}: [{nshots} - ({felix_hz}Hz)]"
        dataToSend["pow"][powerfile['name']] = makeDataToSend(
            wavelength, total_power, powlegend, 
            update={"mode": "markers", "xaxis": "x2", "yaxis": "y2",  "marker": lineColor, **groupItem}
        )            
        ################### Spectrum Analyser END #################################
        ################### Averaged and Normalised Spectrum #################################

        # Normalised Intensity
        defaultStyle={
            "mode": "lines+markers", 
            "fill": 'tozeroy', 
            "marker": {"size":1}, 
            "line":lineColor
        }
        _del = "\u0394"

        felixfile_lg = f"{felixfileName}({_del}:{round(diff(wavelength).mean(), 1)})"
        
        dataToSend["average"][felixfileName] = makeDataToSend(wavelength, intensity, felixfile_lg, update=defaultStyle)
        dataToSend["average_rel"][felixfileName] = makeDataToSend(wavelength_rel, relative_depletion, felixfile_lg, update=defaultStyle)
        dataToSend["average_per_photon"][felixfileName] = makeDataToSend(wavelength, energyJ, felixfile_lg, update=defaultStyle)
        ################### Averaged Spectrum END #################################
        dataToSend["base"][f"{felixfileName}_base"] = makeDataToSend(
            undulatorWn, counts, felixfile['legend'], 
            update={"mode": "lines", "line":lineColor, **groupItem }
        )
       
        dataToSend["base"][f"{felixfileName}_line"] = makeDataToSend(
            baseData[0], baseData[1], felixfileName,
            update={"mode": "lines+markers", "line":blackColor, **groupItem, **nolegend}
        
        )
        counter += 1

    binns, intens = felix_binning(xs, ys, delta)
    energyJ_norm = inten_per_photon(binns, intens)
    binns_r, intens_r = felix_binning(xs_r, ys_r, delta)
    
    defaultStyle={"mode": "lines+markers", "marker": {"size":1}, "line":{"color": "black", "shape":"hv"}}
    felixfile_avg_lg = f"averaged({_del}:{round(diff(binns).mean(), 1)})"

    dataToSend["average"]["average"] = makeDataToSend(binns, intens, felixfile_avg_lg, update=defaultStyle)
    dataToSend["average_rel"]["average"] = makeDataToSend(
        binns_r, intens_r, felixfile_avg_lg,
        update=defaultStyle
    )
    dataToSend["average_per_photon"]["average"] = makeDataToSend(
        binns, energyJ_norm, felixfile_avg_lg,
        update=defaultStyle
    )
    return dumps(dataToSend)

