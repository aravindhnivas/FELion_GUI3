
export default function({groundLevel, excitedLevel, energyLevels, trapTemp=5, electronSpin=false, zeemanSplit=false, energyUnit="cm-1"}={}){
    // defined for excitation rate constants

    const boltzmanConstant = 1.38064852e-23 // in J.K-1
    const boltzmanConstantInWavenumber = boltzmanConstant/1.98630e-23 // in cm-1
    const KT = boltzmanConstantInWavenumber*trapTemp
    
    const speedOfLight = 299792458 // in m/s
    const speedOfLightIn_cm = speedOfLight*100 // in cm/s

    try {
    
        if (energyUnit==="MHz") {
            energyLevels = energyLevels.map(({label, value, id})=>{
                value = (value*1e6)/speedOfLightIn_cm
                return {label, value, id}
            })


        }
        
        const {Gi, Gf} = computeStatisticalWeight({electronSpin, zeemanSplit, final:excitedLevel, initial:groundLevel})
        const Gj = Gf/Gi;

        const energy_levels = {}
        energyLevels.forEach(f=>energy_levels[f.label]=f.value)

        const delE = Math.abs(energy_levels[groundLevel] - energy_levels[excitedLevel])
        const energyTerm = Math.exp(-delE/KT)
        const rateConstant = Gj*energyTerm
        console.log(energyLevels)
        return rateConstant.toExponential(3)
    } catch (error) {
        console.error(error)
        window.createToast("Error occured", "danger")
        return null

    }

}

export function computeStatisticalWeight({electronSpin=false, zeemanSplit=false, final, initial}={}) {

    let Gi, Gf;

    if (!zeemanSplit) {
        if (electronSpin) {

            Gi = 2*+initial.split("_")[1] + 1
            Gf = 2*+final.split("_")[1] + 1
        } else {
            Gi = 2*+initial + 1
            Gf = 2*+final + 1
        }
    } else {Gi=1, Gf=1}
    return {Gi, Gf}

}