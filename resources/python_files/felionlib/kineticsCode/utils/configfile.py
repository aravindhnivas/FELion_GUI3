from typing import Literal
import numpy as np
import json
from pathlib import Path as pt
from felionlib.utils.FELion_definitions import readCodeFromFile

keyFoundForRate = False
k_err: np.ndarray = None
k3Labels: list[str] = []
ratek3: list[float] = []
kCIDLabels: list[str] = []
ratekCID: list[float] = []

rateConstantsFileData: dict[str, dict] = {}
savefile: pt = None

min_max_step_controller: dict[Literal["forwards", "backwards"], dict[str, tuple[float, float, float]]] = None
forwards_labels_and_bounds: dict[str, tuple[float, float, float]] = None
backwards_labels_and_bounds: dict[str, tuple[float, float, float]] = None


def codeToRun(code: str):
    exec(code)
    return locals()


def read_config(
    fit_config_file: pt, selectedFile: str, kinetics_equation_file: pt, useTaggedFile: bool, tagFile: str
) -> None:

    global keyFoundForRate, k_err
    global ratek3, ratekCID
    global rateConstantsFileData
    global savefile
    global min_max_step_controller, forwards_labels_and_bounds, backwards_labels_and_bounds

    savefile = fit_config_file

    codeContents = readCodeFromFile(kinetics_equation_file)
    codeOutput = codeToRun(codeContents)

    min_max_step_controller = codeOutput["min_max_step_controller"]

    forwards_labels_and_bounds = min_max_step_controller["forwards"]
    backwards_labels_and_bounds = min_max_step_controller["backwards"]

    for label, controller in forwards_labels_and_bounds.items():
        k3Labels.append(label)
        ratek3.append((controller[1] - controller[0]) / 2)

    for label, controller in backwards_labels_and_bounds.items():
        kCIDLabels.append(label)
        ratekCID.append((controller[1] - controller[0]) / 2)

    print(f"{k3Labels=}, {kCIDLabels=}", flush=True)

    k3_err = np.zeros_like(ratek3)
    kCID_err = np.zeros_like(ratekCID)
    print(f"{fit_config_file=}: {fit_config_file.exists()=}", flush=True)
    if fit_config_file.exists():

        with open(fit_config_file, "r") as f:
            keyFound = False
            rateConstantsFileContents = f.read()

            if len(rateConstantsFileContents) > 0:

                rateConstantsFileData = json.loads(rateConstantsFileContents)
                print(f"{fit_config_file.name} read: {rateConstantsFileData}", flush=True)

                if selectedFile in rateConstantsFileData:
                    if useTaggedFile:
                        if "tag" in rateConstantsFileData[selectedFile]:
                            if tagFile in rateConstantsFileData[selectedFile]["tag"]:
                                searchContent = rateConstantsFileData[selectedFile]["tag"][tagFile]
                                keyFound = True
                    else:
                        keyFound = True
                        searchContent = rateConstantsFileData[selectedFile]

                print(f"{keyFound=}", flush=True)

            if keyFound:

                k3_fit_keyvalues: dict[str, float] = searchContent["k3_fit"]
                kCID_fit_keyvalues: dict[str, float] = searchContent["kCID_fit"]
                print(f"{k3_fit_keyvalues=}", flush=True)
                print(f"{kCID_fit_keyvalues=}", flush=True)

                for k3_key in k3_fit_keyvalues.keys():

                    if k3_key in k3Labels:

                        k3_found_index = k3Labels.index(k3_key)
                        ratek3[k3_found_index] = float(k3_fit_keyvalues[k3_key][0])
                        k3_err[k3_found_index] = float(k3_fit_keyvalues[k3_key][1])
                        keyFoundForRate = True

                        print(f"setting found value for {k3_key}", flush=True)
                        print(f"{k3_found_index=}\t{float(k3_fit_keyvalues[k3_key][0])=}", flush=True)
                        print(f"{ratek3=}", flush=True)

                for kCID_key in kCID_fit_keyvalues.keys():
                    if kCID_key in kCIDLabels:
                        print(f"setting found value for {kCID_key}", flush=True)
                        kCID_found_index = kCIDLabels.index(kCID_key)
                        ratekCID[kCID_found_index] = float(kCID_fit_keyvalues[kCID_key][0])
                        kCID_err[kCID_found_index] = float(kCID_fit_keyvalues[kCID_key][1])

                        keyFoundForRate = True

    k_err = np.concatenate((k3_err, kCID_err))
    print(f"{k_err=}\n{ratek3=}\n{ratekCID=}", flush=True)
    print(f"{keyFoundForRate=}", flush=True)
