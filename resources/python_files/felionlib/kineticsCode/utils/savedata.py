import json
import traceback
from pathlib import Path as pt
from felionlib.kineticsCode.utils.definitions import formatArray

from felionlib.utils import logger
from felionlib.utils.msgbox import MsgBox, MB_ICONERROR, MB_ICONINFORMATION


def saveData(
    args,
    ratek3,
    k3Labels,
    kCIDLabels,
    k_fit,
    k_err,
    rateCoefficientArgs,
    fitPlot,
    expPlot,
    rateConstantsFileData,
    savefile: pt,
):

    # kinetic_file_location = pt(args["kinetic_file_location"])
    numberDensity = float(args["numberDensity"])
    nameOfReactants = args["nameOfReactantsArray"]
    temp = float(args["temp"])
    selectedFile = args["selectedFile"]

    try:

        logger(f"{formatArray(rateCoefficientArgs[0])=}")
        logger(f"{formatArray(rateCoefficientArgs[1])=}")

        k3Len = len(ratek3)
        with open(savefile, "w+") as f:

            k3Values = formatArray(rateCoefficientArgs[0])
            k3Err = formatArray(k_err[:k3Len]) if len(k_err)>0 else [0] * len(k3Labels)

            kCIDValues = formatArray(rateCoefficientArgs[1])
            kCIDErr = formatArray(k_err[k3Len:]) if len(k_err)>0 else [0] * len(kCIDLabels)

            k3_fit = {key: [value, err] for key, value, err in zip(k3Labels, k3Values, k3Err)}
            kCID_fit = {key: [value, err] for key, value, err in zip(kCIDLabels, kCIDValues, kCIDErr)}

            rateConstantsFileData[selectedFile] = {
                "k3_fit": k3_fit,
                "kCID_fit": kCID_fit,
                "temp": f"{temp:.1f}",
                "numberDensity": f"{numberDensity:.2e}",
            }
            
            logger(f"{rateConstantsFileData[selectedFile]=}")
            data = json.dumps(rateConstantsFileData, sort_keys=True, indent=4, separators=(",", ": "))

            f.write(data)
            logger(f"file written: {savefile.name} in {savefile.parent} folder")

            MsgBox(
                "Saved",
                f"Rate constants written: '{savefile.name}'\nLocation: {savefile.parent}",
                MB_ICONINFORMATION,
            )

        savefilename = savefile.parent / f"../EXPORT/{selectedFile}_fitted.json"
        with open(savefilename, "w+") as f:

            dataToSaveFit = {"fit": {}, "exp": {}}

            for name, fitLine, expLine in zip(nameOfReactants, fitPlot, expPlot):
                xdata_f, ydata_f = fitLine.get_data()
                xdata, ydata = expLine.get_children()[0].get_data()
                dataToSaveFit["fit"][name] = {"xdata": xdata_f.tolist(), "ydata": ydata_f.tolist()}
                dataToSaveFit["exp"][name] = {"xdata": xdata.tolist(), "ydata": ydata.tolist()}

            data = json.dumps(dataToSaveFit, sort_keys=True, indent=4, separators=(",", ": "))
            f.write(data)
            logger(f"file written: {selectedFile}_fitted.json in EXPORT folder")

    except Exception:
        error = traceback.format_exc(5)
        MsgBox("Error occured: ", f"Error occured while saving the file\n{error}", MB_ICONERROR)
