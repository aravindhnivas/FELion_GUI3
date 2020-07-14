
import {felixOutputName, plotlyEventCreatedOPO, get} from './svelteWritables';
import {plot} from "../../../js/functions.js";
import {plotlySelection, plotlyClick} from "./misc";
export function opofile_func({dataFromPython}={}) {

    felixOutputName.set("averaged")

    plot("OPO spectrum", "Wavenumber (cm-1)", "Counts", dataFromPython["real"], "opoplot")
    plot("OPO Calibration", "Set Wavenumber (cm-1)", "Measured Wavenumber (cm-1)", dataFromPython["SA"], "opoSA")
    plot("OPO spectrum: Depletion (%)", "Wavenumber (cm-1)", "Depletion (%)", dataFromPython["relative"], "opoRelPlot")


    if(!get(plotlyEventCreatedOPO)){
        const plot = {graphDiv:"opoRelPlot", mode:"opo"}
        plotlySelection(plot), plotlyClick(plot);

        plotlyEventCreatedOPO.set(true)

    }
}