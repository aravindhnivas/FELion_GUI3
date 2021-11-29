
function computeKineticCodeScipy({nameOfReactants, ratek3, ratekCID}) {

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

function computeKineticCodeSympy({initialValues, nameOfReactants, ratek3, ratekCID}) {

    
    const nameOfReactantsArr = nameOfReactants.split(",").map(name => name.trim())
    const rateForwardArr = ratek3.split(",").map(name => name.trim())
    const rateReverseArr = ratekCID.split(",").map(name => name.trim())

    let dataToSave = []
    let dataToSet = ""

    ///////////////////////////////////////////////////////////////////////
    
    dataToSet += "## Defining initial variables and parameters\n"
    dataToSet += "```plaintext\n"

    dataToSet += `${nameOfReactantsArr.join(", ")}, t = variables("${nameOfReactantsArr.join(", ")}, t")\n`
    dataToSet += `${ratek3} = parameters("${ratek3}")\n`
    dataToSet += `${ratekCID} = parameters("${ratekCID}")\n`
    dataToSet += "```\n---\n"
    /////////////////////////////////////////////////////////////////////////
    
    
    /////////////////////////////////////////////////////////////////////////
    dataToSet += "## Initial Condition\n"
    dataToSet += "```plaintext\n"
    dataToSet += "initial_condition = {\n\tt: 0,\n\t"

    dataToSave = initialValues.map((value, index) => {
        return `${nameOfReactantsArr[index]} : ${value},`

    })

    dataToSet += `${dataToSave.join("\n\t")}`

    dataToSet += "\n}\n"
    dataToSet += "```\n---\n"
    /////////////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////////////
    dataToSet += "## Defining formation rate equations\n"
    dataToSet += "```plaintext\n"
    
    for (let index = 0; index < nameOfReactantsArr.length-1; index++) {
        const currentMolecule = nameOfReactantsArr[index]
        const nextMolecule = nameOfReactantsArr[index+1]
        dataToSet += `${currentMolecule}_f = -(${rateForwardArr[index]} * ${currentMolecule})`
        dataToSet += `+ (${rateReverseArr[index]} * ${nextMolecule})\n`
    }

    dataToSet += "```\n---\n"
    /////////////////////////////////////////////////////////////////////////

    /////////////////////////////////////////////////////////////////////////
    dataToSet += "## Defining rate model\n"
    dataToSet += "```plaintext\n"

    dataToSet += `rate_model = {\n\tD(${nameOfReactantsArr.at(0)}, t): ${nameOfReactantsArr.at(0)}_f,\n`

    for (let index = 1; index < nameOfReactantsArr.length - 1; index++) {
        const currentMolecule = nameOfReactantsArr[index]
        const prevMolecule = nameOfReactantsArr[index-1]
        dataToSet += `\tD(${currentMolecule}, t): ${currentMolecule}_f - ${prevMolecule}_f,\n`
    }

    dataToSet += `\tD(${nameOfReactantsArr.at(-1)}, t): - ${nameOfReactantsArr.at(-2)}_f\n}\n`
    

    dataToSet += "ode_model = ODEModel(rate_model, initial=initial_condition)\n"
    dataToSet += "```\n---\n"
    ///////////////////////////////////////////////////////////////////////

    return dataToSet
}
export {computeKineticCodeScipy, computeKineticCodeSympy}