import {fill} from "lodash-es"
export function getEnergyLabels({numberOfLevels=2, electronSpin=false, zeemanSplit=false}={}){
    const value=0
    const energyLevelsInfo = fill(Array(numberOfLevels)).map((_, i)=>i).map((N, i)=>{
        if (electronSpin) {
            const splitLevels = [-0.5, 0.5]
            N = []
            splitLevels.forEach(s=>{
                const current_J = i+s
                if (current_J>0) {
                    if (zeemanSplit) {
                        let mJ = []
                        for (let current_mJ=current_J; current_mJ >= -current_J; current_mJ--) {
                            mJ = [...mJ, {label:`${i}_${current_J}__${current_mJ}`, value, id:window.getID()}]
                        } 
                        N = [...N, mJ]
                    } else {N = [...N, {label:`${i}_${current_J}`, value, id:window.getID()}]}
                }

            })

            return N

        } else {return {label:i, value, id:window.getID()}}
    })

    const energyLevels = energyLevelsInfo.flat(Infinity)
    return {energyLevels, energyLevelsInfo}
}