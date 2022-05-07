import numpy as np
import json
from pathlib import Path as pt



keyFoundForRate = False
k_err: np.ndarray = None
ratek3: np.ndarray = None
ratekCID: np.ndarray = None
rateConstantsFileData = {}
savefile: pt = None


def read_config(
        fit_config_file: pt, selectedFile: str, k3Guess: float, kCIDGuess: float, k3Labels: list[str], kCIDLabels: list[str]
    ) -> None:
    
    
    global keyFoundForRate, k_err
    global ratek3, ratekCID
    global rateConstantsFileData
    global savefile
    
    savefile = fit_config_file
    
    ratek3 = [float(k3Guess) for _ in k3Labels]
    ratekCID = [float(kCIDGuess) for _ in kCIDLabels]
    k3_err = [0]*len(ratek3)
    kCID_err = [0]*len(ratekCID)
    
    if fit_config_file.exists():
    
        with open(fit_config_file, "r") as f:

            keyFound = False
            rateConstantsFileContents = f.read()

            if len(rateConstantsFileContents) > 0:

                rateConstantsFileData = json.loads(rateConstantsFileContents)
                print(rateConstantsFileData, flush=True)

                keyFound = selectedFile in rateConstantsFileData
                print(f"{keyFound=}", flush=True)

            if keyFound:

                k3_fit_keyvalues: dict[str, float] = rateConstantsFileData[selectedFile]["k3_fit"]
                kCID_fit_keyvalues: dict[str, float] = rateConstantsFileData[selectedFile]["kCID_fit"]
                
                for k3_key in k3_fit_keyvalues.keys():
                    
                    if k3_key in k3Labels:
                        k3_found_index = k3Labels.index(k3_key)
                        ratek3[k3_found_index] = float(k3_fit_keyvalues[k3_key][0])
                        k3_err[k3_found_index] = float(k3_fit_keyvalues[k3_key][1])
                        
                        keyFoundForRate = True
                        
                for kCID_key in kCID_fit_keyvalues.keys():
                    
                    if kCID_key in kCIDLabels:
                        kCID_found_index = kCIDLabels.index(kCID_key)
                        ratekCID[kCID_found_index] = float(kCID_fit_keyvalues[kCID_key][0])
                        kCID_err[kCID_found_index] = float(kCID_fit_keyvalues[kCID_key][1])
                        keyFoundForRate = True
    k_err = np.concatenate((k3_err, kCID_err))
    print(f"{k_err=}", flush=True)
    