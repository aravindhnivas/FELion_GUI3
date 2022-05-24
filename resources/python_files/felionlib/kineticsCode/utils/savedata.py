import json
import traceback

# from felionlib.kineticsCode.utils.definitions import formatArray
from felionlib.utils import logger
from felionlib.utils.msgbox import MsgBox, MB_ICONERROR, MB_ICONINFORMATION
from felionlib.kineticsCode import selectedFile, nameOfReactants, useTaggedFile, tagFile


def saveData():

    try:

        from .fit import rateCoefficientArgs, k_err
        from .plot import fitPlot, expPlot
        from .configfile import ratek3, rateConstantsFileData, savefile, k3Labels, kCIDLabels

        logger(f"{rateCoefficientArgs[0]=}")
        logger(f"{rateCoefficientArgs[1]=}")

        k3Len = len(ratek3)
        with open(savefile, "w+") as f:

            k3Values = rateCoefficientArgs[0]
            k3Err = k_err[:k3Len]

            kCIDValues = rateCoefficientArgs[1]
            kCIDErr = k_err[k3Len:]

            # precession = 4
            k3_fit = {key: [value, err] for key, value, err in zip(k3Labels, k3Values, k3Err)}
            kCID_fit = {key: [value, err] for key, value, err in zip(kCIDLabels, kCIDValues, kCIDErr)}

            print(f"{rateConstantsFileData=}", flush=True)

            save_data = {
                "k3_fit": k3_fit,
                "kCID_fit": kCID_fit,
            }

            # tag_data = {}
            current_data = {"tag": {}}

            if selectedFile in rateConstantsFileData:
                current_data = rateConstantsFileData[selectedFile]
                if "tag" not in current_data:
                    current_data["tag"] = {}

            if useTaggedFile:
                current_data["tag"][tagFile] = save_data
            else:
                if "tag" in current_data:
                    save_data = save_data | {"tag": current_data["tag"]}
                current_data = save_data

            rateConstantsFileData[selectedFile] = current_data
            print(f"{rateConstantsFileData=}", flush=True)
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
