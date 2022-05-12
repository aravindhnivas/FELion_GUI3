export class computeKineticCodeScipy {

    constructor({ nameOfReactants, ratek3, ratekCID, k3Guess, kCIDGuess, loss_channels }) {
        this.nameOfReactants = nameOfReactants
        this.ratek3 = ratek3
        this.ratekCID = ratekCID
        this.k3Guess = k3Guess
        this.kCIDGuess = kCIDGuess
        this.loss_channels = loss_channels
        this.nameOfReactantsArr = nameOfReactants
            .split(',')
            .map((name) => name.trim())

        const rateForwardArr_keys = ratek3.split(',').map((name) => name.trim())
        const forwards_loss_channels_keys = loss_channels.filter(({type}) => type === 'forwards').map(({name}) => name)
        this.rateForwardArr = [...rateForwardArr_keys, ...forwards_loss_channels_keys]

        const rateReverseArr_keys = ratekCID.split(',').map((name) => name.trim())
        const backwards_loss_channels_keys = loss_channels.filter(({type}) => type === 'backwards').map(({name}) => name)
        this.rateReverseArr = [...rateReverseArr_keys, ...backwards_loss_channels_keys]
    } 
    get sliders() {
        let data = ''
        data += '## Defining min-max-value for sliders\n'
        data += '```plaintext\n'
        data += '\nmin_max_step_controller = {}\n'
        data += '\nmin_max_step_controller["forwards"] = {\n'
        this.rateForwardArr.forEach((value) => {
            data += `\t'${value}': (${this.k3Guess}, 1e-3),\n`
        })
        data += '}\n'
        
        data += '\nmin_max_step_controller["backwards"] = {\n'
        this.rateReverseArr.forEach((value) => {
            data += `\t'${value}': (${this.kCIDGuess}, 1e-3),\n`
        })
        data += '}\n'
        data += '```\n'
        return data
    }
    
    get model() {
        let data = ''
    
        data += '## Defining ODE model\n'
        data += '```plaintext\n'
        data += 'def compute_attachment_process(t, N):\n\n'
        data += '\tk3, kCID = rateCoefficientArgs\n\n'
        data += `\t${this.rateForwardArr.join(', ')}${
            this.rateForwardArr.length == 1 ? ',' : ''
        } = k3\n`
        data += `\t${this.rateReverseArr.join(', ')}${
            this.rateReverseArr.length == 1 ? ',' : ''
        } = kCID\n\n`
    
        data += `\t${this.nameOfReactantsArr.join(', ')} = N\n\n`
    
        for (let index = 0; index < this.nameOfReactantsArr.length - 1; index++) {
            const currentMolecule = this.nameOfReactantsArr[index]
            const nextMolecule = this.nameOfReactantsArr[index + 1]
            data += `\t${currentMolecule}_f = -(${this.rateForwardArr[index]} * ${currentMolecule})`
            data += `+ (${this.rateReverseArr[index]} * ${nextMolecule})\n`
        }
        data += `\n\tdNdT = [\n`
        data += this.make_final_list()
        data += `\t]\n\n`
        data += `\treturn dNdT\n`
        data += '```\n---\n'
        return data
    
    }
    make_final_list() {

        const parentMolecule = this.nameOfReactantsArr.at(0)
        let data = [`\t\t${parentMolecule}_f,\n`]
    
        for (let index = 1; index < this.nameOfReactantsArr.length - 1; index++) {
            const currentMolecule = this.nameOfReactantsArr[index]
            const prevMolecule = this.nameOfReactantsArr[index - 1]
            data.push(`\t\t${currentMolecule}_f - ${prevMolecule}_f,\n`)
        }
        data.push(`\t\t- ${this.nameOfReactantsArr.at(-2)}_f\n`)
        if(this.loss_channels.length === 0) return data.join('')
    
        const trim_this_line = (line) => line.trimEnd().replace(',', '')
        data[0] = trim_this_line(data[0])
        this.loss_channels.forEach(({name, attachTo}) => {
            const loss_reaction = `(${name} * ${parentMolecule})`
            data[0] += ` - ${loss_reaction}`
            if(attachTo === 'none') return
            const attachIndex = this.nameOfReactantsArr.indexOf(attachTo)
            data[attachIndex] = trim_this_line(data[attachIndex]) + ` + ${loss_reaction},\n`
        })
        data[0] += ',\n'
        return data.join('')
    }

    get fullEquation() {
        return this.sliders + this.model
    }
}