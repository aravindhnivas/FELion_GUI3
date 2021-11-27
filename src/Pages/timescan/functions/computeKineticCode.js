
export default function computeKineticCode({massOfReactants, nameOfReactants, ratek3, ratekCID}) {

    const nameOfReactantsArr = nameOfReactants.split(",").map(name => name.trim())
    const rateForwardArr = ratek3.split(",").map(name => name.trim())
    const rateReverseArr = ratekCID.split(",").map(name => name.trim())

    let dataToSet = "# Kinetics code\n"

    /////////////////////////////////////////////////////////////////////////

    if (rateForwardArr.length !== rateReverseArr.length) {
        dataToSet += "## Defining min-max-value for new slider\n"
        dataToSet += "```plaintext\nkvalueLimits = {\n\t'label': (min, max, value)\n}\n"
        dataToSet += "```\n"

    }
    dataToSet += "## Defining ODE model\n"
    dataToSet += "```plaintext\n"

    dataToSet += "def compute_attachment_process(t, N):\n\n"
    dataToSet += "\tk3, kCID = rateCoefficientArgs\n\n"
    dataToSet += `\t${rateForwardArr.join(", ")}${rateForwardArr.length == 1 ? "," : ""} = k3\n`
    dataToSet += `\t${rateReverseArr.join(", ")}${rateReverseArr.length == 1 ? "," : ""} = kCID\n\n`

    dataToSet += `\t${nameOfReactantsArr.join(", ")} = N\n\n`
    
    for (let index = 0; index < nameOfReactantsArr.length-1; index++) {
    
        const currentMolecule = nameOfReactantsArr[index]
        const nextMolecule = nameOfReactantsArr[index+1]
        dataToSet += `\t${currentMolecule}_f = -(${rateForwardArr[index]} * numberDensity**2 * ${currentMolecule})`
        dataToSet += `+ (${rateReverseArr[index]} * numberDensity * ${nextMolecule})\n`
    
    }

    dataToSet += `\n\tdNdT = [\n\t\t${nameOfReactantsArr.at(0)}_f,\n`
    for (let index = 1; index < nameOfReactantsArr.length - 1; index++) {
        const currentMolecule = nameOfReactantsArr[index]
        const prevMolecule = nameOfReactantsArr[index-1]
        dataToSet += `\t\t${currentMolecule}_f - ${prevMolecule}_f,\n`
    }

    dataToSet += `\t\t- ${nameOfReactantsArr.at(-2)}_f\n\t]\n\n`

    dataToSet += `\treturn dNdT\n`

    dataToSet += "```\n---\n"

    /////////////////////////////////////////////////////////////////////////
    dataToSet += "\n\n"
    return dataToSet

}