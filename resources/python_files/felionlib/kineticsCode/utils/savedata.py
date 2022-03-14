import json
import traceback
from pathlib import Path as pt
from felionlib.kineticsCode.utils.definitions import log, formatArray
from felionlib.utils.msgbox import MsgBox, MB_ICONERROR, MB_ICONINFORMATION


def saveData(
    event, widget, args,
    ratek3, k3Labels, kCIDLabels,
    k_fit, k_err, rateCoefficientArgs,
    fitPlot, expPlot, rateConstantsFileData
):

    currentLocation = pt(args["currentLocation"]).parent
    savedir = currentLocation/"OUT"
    savefile = savedir/"k_fit.json"

    numberDensity = float(args["numberDensity"])
    nameOfReactants = args["nameOfReactantsArray"]
    temp = float(args["temp"])
    selectedFile = args["selectedFile"]

    try:

        k3Len = len(ratek3)

        with open(savefile, "w+") as f:

            k3Values = (
                formatArray(rateCoefficientArgs[0]),
                formatArray(k_fit[:k3Len])
            )[len(k_fit) > 0]

            k3Err = ([0]*len(k3Labels),
                     formatArray(k_err[:k3Len]))[len(k_err) > 0]

            kCIDValues = (
                formatArray(rateCoefficientArgs[1]),
                formatArray(k_fit[k3Len:])
            )[len(k_fit) > 0]

            kCIDErr = ([0]*len(kCIDLabels),
                       formatArray(k_err[k3Len:]))[len(k_err) > 0]

            k3_fit = {
                key: [value, err]
                for key, value, err in zip(k3Labels, k3Values,  k3Err)
            }
            kCID_fit = {
                key: [value, err]
                for key, value, err in zip(kCIDLabels, kCIDValues, kCIDErr)
            }

            dataToSave = {selectedFile: {}}
            dataToSave[selectedFile] = {
                "k3_fit": k3_fit,
                "kCID_fit": kCID_fit,
                "temp": f"{temp:.1f}",
                "numberDensity": f"{numberDensity:.2e}"
            }

            data = json.dumps(
                {**rateConstantsFileData, **dataToSave},
                sort_keys=True, indent=4, separators=(',', ': ')
            )

            f.write(data)
            log(f"file written: {savefile.name} in {currentLocation} folder")

            MsgBox(
                "Saved",
                f"Rate constants written in json format : '{savefile.name}'\nLocation: {currentLocation}", MB_ICONINFORMATION
            )

            
        savefilename = currentLocation/f"EXPORT/{selectedFile}_fitted.json"
        with open(savefilename, "w+") as f:
            dataToSaveFit = {
                "fit": {},
                "exp": {}
            }

            for name, fitLine, expLine in zip(nameOfReactants, fitPlot, expPlot):

                xdata_f, ydata_f = fitLine.get_data()
                xdata, ydata = expLine.get_children()[0].get_data()

                dataToSaveFit["fit"][name] = {
                    "xdata": xdata_f.tolist(),
                    "ydata": ydata_f.tolist()
                }

                dataToSaveFit["exp"][name] = {
                    "xdata": xdata,
                    "ydata": ydata
                }

            data = json.dumps(
                dataToSaveFit, sort_keys=True,
                indent=4, separators=(',', ': ')
            )

            f.write(data)

            log(f"file written: {selectedFile}_fitted.json in EXPORT folder")

    except Exception:
        error = traceback.format_exc(5)
        MsgBox(
            "Error occured: ",

            f"Error occured while saving the file\n{error}",
            MB_ICONERROR
        )

        log(f"Error occured while saving the file\n{error}")
