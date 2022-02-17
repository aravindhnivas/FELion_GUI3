
import {sumBy} from "lodash-es"
import {boltzmanConstantInMHz, boltzmanConstantInWavenumber} from "./constants";
export default function({energyLevels=[], trapTemp=5, electronSpin=false, zeemanSplit=false, energyUnit="cm-1"}={}){
    const kB = {
        "MHz": boltzmanConstantInMHz,
        "cm-1": boltzmanConstantInWavenumber
    }

    const KT = kB[energyUnit]*trapTemp

    try {

      
        //  Checking if value is in "00_00_00" number format
        energyLevels = energyLevels.map(({label, value})=> {
            if ( typeof value === "string") {
                if (value.includes("_")) {value = parseFloat(value.replaceAll("_", ""))}
                else {value = parseFloat(value)}
            }
            return {label, value}
        })

        
        let distribution = energyLevels.map(({label, value:currentEnergy})=>{
            let Gj;
            if (electronSpin) {
                if (zeemanSplit) {Gj = 1}
                else {
                    const j = parseFloat(label.split("_")[1])
                    Gj = parseInt( 2*+j + 1 )
                }
            } else {
                if (zeemanSplit) {Gj = 1}
                else {Gj = parseInt( 2*+label + 1 )}
            }
            const value = Gj*Math.exp(-currentEnergy/KT)
            return {label, value}
        })

        const partitionValue = Number(sumBy(distribution, energy=>energy.value)).toFixed(2)
        distribution = distribution.map(({label, value})=>{
            value /= partitionValue
            return {label, value}
        })
        return distribution
    } catch (error) {return error}
}