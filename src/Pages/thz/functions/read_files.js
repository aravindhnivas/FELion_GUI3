
import {tick} from "svelte";
import {browse} from "../../../components/Layout.svelte";

export async function readFromFile({energyFilename=null, electronSpin, zeemanSplit, energyUnit, twoLabel=false}={}){
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

    let ground, excited;
    fileContents.forEach(line=>{
        if (line.length>1){
            
            if (line.includes("//")){
                if (line.includes("units")){energyUnit=line.split("=")[1].trim()}

            } else if (line.includes("#") && (electronSpin||zeemanSplit)){
                let currentLineLabel = line.split("#")[1]
                if (twoLabel) {
                    preLabel  = currentLineLabel.split("\t").map(f=>f.trim())
                }
                else {
                    preLabel = currentLineLabel.trim()
                    numberOfLevels++

                }

            } else {
                
                if (!electronSpin && !zeemanSplit) {
                    line = line.split("\t").map(f=>f.trim())

                    if (twoLabel) {
                        [ground, excited] = preLabel
                        label = `${excited} --> ${ground}`
                        value = line[0].trim()
                    } else {
                        
                        label = numberOfLevels
                        numberOfLevels++
                        value = line[0].trim()
                        
                    }

                } else {
                    line = line.split("\t").map(f=>f.trim())

                    const separator = electronSpin&&zeemanSplit ? "__" : "_"
                    if (twoLabel) {
                        [ground, excited] = preLabel

                        label = `${excited}${separator}${line[1]} --> ${ground}${separator}${line[0]}`

                    } else {
                        value = line[1]

                        label = preLabel+separator+line[0]
                    }
                }

                energyLevels = [...energyLevels, {label, value, id:window.getID()}]

            }
        }

    })

    await tick()

    window.createToast("Energy file read: "+path.basename(energyFilename))

    return Promise.resolve({energyLevels, numberOfLevels, energyFilename, energyUnit})
}