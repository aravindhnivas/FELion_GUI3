
export default function({energyLevels, trapTemp=5, electronSpin=false, zeemanSplit=false, energyUnit="cm-1"}={}){
    const boltzmanConstant = 1.38064852e-23 // in m2.kg.s-2.K-1
    const boltzmanConstantInWavenumber = boltzmanConstant/1.98630e-23 // in cm-1
    const KT = boltzmanConstantInWavenumber*trapTemp
    const speedOfLight = 299792458 // in m/s
    const speedOfLightIn_cm = speedOfLight*100 // in cm/s

    try {

        // console.log(energyLevels)
        
        
        energyLevels = energyLevels.map(({label, value})=> {
            if ( typeof value === "string") {
                if (value.includes("_")) {value = parseFloat(value.replaceAll("_", ""))}
                else {value = parseFloat(value)}
            }
            
            
            return {label, value}
        })


        if (energyUnit==="MHz") {
            energyLevels = energyLevels.map(({label, value})=>{
                value = (value*1e6)/speedOfLightIn_cm
                return {label, value}
            })

        }
        
        let distribution = energyLevels.map(({label, value:currentEnergy})=>{
            let Gj;
            if (electronSpin) {
                if (zeemanSplit) {Gj = 1}
                else {
                    j = label.split("_")[1]
                    Gj = parseInt( 2*+j + 1 )
                }
            } else {
                if (zeemanSplit) {Gj = 1}
                else {Gj = parseInt( 2*+label + 1 )}
            }
            const value = Gj*Math.exp(-currentEnergy/KT)
            return {label, value}
        })


        // console.log(distribution)
        const partitionValue = _.sumBy(distribution, energy=>energy.value).toFixed(2)

        distribution = distribution.map(({label, value})=>{
            value /= partitionValue
            return {label, value}
        })
        return distribution
    } catch (error) {return error}
}