
export default function({groundLevel, excitedLevel, energyLevels, trapTemp=5, electronSpin=false, zeemanSplit=false, energyUnit="cm-1"}={}){
    // defined for excitation rate constants

    const boltzmanConstant = 1.38064852e-23 // in m2.kg.s-2.K-1
    const boltzmanConstantInWavenumber = boltzmanConstant/1.98630e-23 // in cm-1
    const KT = boltzmanConstantInWavenumber*trapTemp
    
    const speedOfLight = 299792458 // in m/s
    const speedOfLightIn_cm = speedOfLight*100 // in cm/s

    try {
    
        energyLevels = energyLevels.map(({label, value, id})=> {
            value = parseFloat(value)
            return {label, value, id}
        
        })
        
        
        if (energyUnit==="MHz") {
            energyLevels = energyLevels.map(({label, value, id})=>{
                value = (value*1e6)/speedOfLightIn_cm
                return {label, value, id}
            })

        }

        const energy_levels = {}
        energyLevels.forEach(f=>energy_levels[f.label]=f.value)
        let N0, N1, Gj;
        if (electronSpin) {
            if (zeemanSplit) {Gj = 1}
            else {

                N0 = 2*+groundLevel.split("_")[1] + 1

                N1 = 2*+excitedLevel.split("_")[1] + 1

                Gj = N1/N0
            }
        } else {
            if (zeemanSplit) {Gj = 1}


            else {

                N0 = 2*+groundLevel + 1
                N1 = 2*+excitedLevel + 1
                Gj = N1/N0
            }
        }

        const delE = Math.abs(energy_levels[groundLevel] - energy_levels[excitedLevel])

        const energyTerm = Math.exp(-delE/KT)
        const rateConstant = Gj*energyTerm

        console.log(KT, groundLevel, excitedLevel, delE.toFixed(2), energyTerm, Gj.toFixed(2), rateConstant)
        return rateConstant.toExponential(3)
    } catch (error) {

        console.error(error)

        window.createToast("Error occured", "danger")
        return null

    }

}