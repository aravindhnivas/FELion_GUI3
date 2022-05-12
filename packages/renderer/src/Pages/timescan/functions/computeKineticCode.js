const make_final_list = (nameOfReactantsArr, loss_channels=[]) => {

    const parentMolecule = nameOfReactantsArr.at(0)
    let data = [`\t\t${parentMolecule}_f,\n`]

    for (let index = 1; index < nameOfReactantsArr.length - 1; index++) {
        const currentMolecule = nameOfReactantsArr[index]
        const prevMolecule = nameOfReactantsArr[index - 1]
        data.push(`\t\t${currentMolecule}_f - ${prevMolecule}_f,\n`)
    }
    data.push(`\t\t- ${nameOfReactantsArr.at(-2)}_f\n`)
    if(loss_channels.length === 0) return data.join('')

    const trim_this_line = (line) => line.trimEnd().replace(',', '')
    data[0] = trim_this_line(data[0])
    loss_channels.forEach(({name, attachTo}) => {
        const loss_reaction = `(${name} * ${parentMolecule})`
        data[0] += ` - ${loss_reaction}`
        if(attachTo === 'none') return
        const attachIndex = nameOfReactantsArr.indexOf(attachTo)
        data[attachIndex] = trim_this_line(data[attachIndex]) + ` + ${loss_reaction},\n`
    })
    data[0] += ',\n'
    return data.join('')
}

export function computeKineticCodeScipy({ nameOfReactants, ratek3, ratekCID, k3Guess, kCIDGuess, loss_channels }) {
    const nameOfReactantsArr = nameOfReactants
        .split(',')
        .map((name) => name.trim())
    const rateForwardArr_keys = ratek3.split(',').map((name) => name.trim())
    const forwards_loss_channels_keys = loss_channels.filter(({type}) => type === 'forwards').map(({name}) => name)
    const rateForwardArr = [...rateForwardArr_keys, ...forwards_loss_channels_keys]

    const rateReverseArr_keys = ratekCID.split(',').map((name) => name.trim())
    const backwards_loss_channels_keys = loss_channels.filter(({type}) => type === 'backwards').map(({name}) => name)
    const rateReverseArr = [...rateReverseArr_keys, ...backwards_loss_channels_keys]
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

    dataToSet += `\n\tdNdT = [\n`
    dataToSet += make_final_list(nameOfReactantsArr, loss_channels)
    dataToSet += `\t]\n\n`

    dataToSet += `\treturn dNdT\n`
    dataToSet += '```\n---\n'
    dataToSet += '\n\n'
    return dataToSet
    /////////////////////////////////////////////////////////////////////////
}
