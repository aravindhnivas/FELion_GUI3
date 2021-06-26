
import {tick} from "svelte";
import {browse} from "../../../components/Layout.svelte";

export async function readEnergyFromFile({energyFilename=null, electronSpin, zeemanSplit, energyUnit}={}){
    if (!energyFilename) {
        const energyDetailsFile = await browse({dir:false, multiple:false})

        if (energyDetailsFile.filePaths.length==0) return;
        energyFilename = energyDetailsFile.filePaths[0]
    
    }

    const fileContents = fs.readFileSync(energyFilename, "utf-8").split("\n")
    let energyLevels = []

    let preLabel;
    let value, label;
    let numberOfLevels = 0


    fileContents.forEach(line=>{
        if (line.length>1){
            
            if (line.includes("//")){
                if (line.includes("units")){energyUnit=line.split("=")[1].trim()}

            } else if (line.includes("#") && (electronSpin||zeemanSplit)){
                    preLabel = line.split("#")[1].trim()
                    numberOfLevels++

            } else {

                
                if (!electronSpin && !zeemanSplit) {
                    value = line.trim()
                    label = numberOfLevels
                    numberOfLevels++
                } else {
                    line = line.split("\t").map(f=>f.trim())
                    value = line[1]
                    const separator = electronSpin&&zeemanSplit ? "__" : "_"
                    label = preLabel+separator+line[0]
                }
                energyLevels = [...energyLevels, {label, value, id:window.getID()}]
            }
        }
    })

    await tick()
    window.createToast("Energy file read: "+path.basename(energyFilename))
    return Promise.resolve({energyLevels, numberOfLevels, energyFilename, energyUnit})

}