export function computeKineticCodeScipy({ nameOfReactants, ratek3, ratekCID, k3Guess, kCIDGuess }) {
    const nameOfReactantsArr = nameOfReactants
        .split(',')
        .map((name) => name.trim())
    const rateForwardArr = ratek3.split(',').map((name) => name.trim())
    const rateReverseArr = ratekCID.split(',').map((name) => name.trim())
    let dataToSet = '# Kinetics code\n'

    /////////////////////////////////////////////////////////////////////////
    
    dataToSet += '## Defining min-max-value for sliders\n'
    dataToSet += '```plaintext\n'
    dataToSet += '\nmin_max_step_controller = {}\n'
    dataToSet += '\nmin_max_step_controller["forwards"] = {\n'
    rateForwardArr.forEach((value) => {
        dataToSet += `\t'${value}': (${k3Guess}, 1e-3),\n`
    })
    
    dataToSet += '}\n'
    
    dataToSet += '\nmin_max_step_controller["backwards"] = {\n'
    rateReverseArr.forEach((value) => {
        dataToSet += `\t'${value}': (${kCIDGuess}, 1e-3),\n`
    })
    dataToSet += '}\n'
    dataToSet += '```\n'

    /////////////////////////////////////////////////////////////////////////

    dataToSet += '## Defining ODE model\n'
    dataToSet += '```plaintext\n'

    dataToSet += 'def compute_attachment_process(t, N):\n\n'
    dataToSet += '\tk3, kCID = rateCoefficientArgs\n\n'
    dataToSet += `\t${rateForwardArr.join(', ')}${
        rateForwardArr.length == 1 ? ',' : ''
    } = k3\n`
    dataToSet += `\t${rateReverseArr.join(', ')}${
        rateReverseArr.length == 1 ? ',' : ''
    } = kCID\n\n`

    dataToSet += `\t${nameOfReactantsArr.join(', ')} = N\n\n`

    for (let index = 0; index < nameOfReactantsArr.length - 1; index++) {
        const currentMolecule = nameOfReactantsArr[index]
        const nextMolecule = nameOfReactantsArr[index + 1]
        dataToSet += `\t${currentMolecule}_f = -(${rateForwardArr[index]} * ${currentMolecule})`
        dataToSet += `+ (${rateReverseArr[index]} * ${nextMolecule})\n`
    }

    const parentMolecule = nameOfReactantsArr.at(0)
    dataToSet += `\n\tdNdT = [\n\t\t${parentMolecule}_f${ratek3.includes('k_loss') ? ' - k_loss * ' + parentMolecule: ''},\n`
    for (let index = 1; index < nameOfReactantsArr.length - 1; index++) {
        const currentMolecule = nameOfReactantsArr[index]
        const prevMolecule = nameOfReactantsArr[index - 1]
        dataToSet += `\t\t${currentMolecule}_f - ${prevMolecule}_f,\n`
    }
    dataToSet += `\t\t- ${nameOfReactantsArr.at(-2)}_f\n\t]\n\n`

    dataToSet += `\treturn dNdT\n`
    dataToSet += '```\n---\n'
    /////////////////////////////////////////////////////////////////////////
    dataToSet += '\n\n'
    return dataToSet
    
}
