
import type { loss_channelsType } from '$src/Pages/timescan/types/types'

export interface ComputeKineticCodeType {
    nameOfReactants: string;
    ratek3: string;
    ratekCID: string;
    k3Guess: string;
    kCIDGuess: string;
    loss_channels: loss_channelsType;
    includeTrapLoss: boolean;
}

export class computeKineticCodeScipy {

    nameOfReactants: string
    ratek3: string
    ratekCID: string
    k3Guess: string
    kCIDGuess: string
    loss_channels: loss_channelsType
    includeTrapLoss: boolean
    nameOfReactantsArr: string[]
    rateForwardArr: string[]
    rateReverseArr: string[]

    constructor(maindata: ComputeKineticCodeType) {
        
        this.nameOfReactants = maindata.nameOfReactants
        this.ratek3 = maindata.ratek3
        this.ratekCID = maindata.ratekCID
        this.k3Guess = maindata.k3Guess
        this.kCIDGuess = maindata.kCIDGuess
        this.loss_channels = maindata.loss_channels
        this.includeTrapLoss = maindata.includeTrapLoss

        this.nameOfReactantsArr = this.nameOfReactants.split(',').map((name) => name.trim())

        // const rateForwardArr_keys = this.ratek3.split(',').map((name) => name.trim())
        const forwards_loss_channels_keys = this.loss_channels
            .filter(({ type }) => type === 'forwards')
            .map(({ name }) => name)
        
            // this.rateForwardArr = [...rateForwardArr_keys, ...forwards_loss_channels_keys]
            this.rateForwardArr = [...forwards_loss_channels_keys]

        // const rateReverseArr_keys = this.ratekCID.split(',').map((name) => name.trim())
        const backwards_loss_channels_keys = this.loss_channels
            .filter(({ type }) => type === 'backwards')
            .map(({ name }) => name)
        // this.rateReverseArr = [...rateReverseArr_keys, ...backwards_loss_channels_keys]
        this.rateReverseArr = [...backwards_loss_channels_keys]

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
        
        if(this.includeTrapLoss) {
            data += `\t'ktrap_loss': (${this.k3Guess}, 1e-3),\n`
        }
        
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
        data += `\t${this.rateForwardArr.join(', ')}${this.rateForwardArr.length == 1 ? ',' : ''}`
        if(this.includeTrapLoss) {
            if(!data.trim().endsWith(',')) {
                data += ', '
            }
            data += `ktrap_loss`
        }
        data += ' = k3\n'
        data += `\t${this.rateReverseArr.join(', ')}${this.rateReverseArr.length == 1 ? ',' : ''} = kCID\n\n`

        // data += `\t${this.nameOfReactantsArr.join(', ')} = N\n\n`
        data += `\t${this.nameOfReactantsArr.join(', ')} = N\n`

        // for (let index = 0; index < this.nameOfReactantsArr.length - 1; index++) {
        //     const currentMolecule = this.nameOfReactantsArr[index]
        //     const nextMolecule = this.nameOfReactantsArr[index + 1]
        //     data += `\t${currentMolecule}_f = -(${this.rateForwardArr[index]} * ${currentMolecule})`
        //     data += ` + (${this.rateReverseArr[index]} * ${nextMolecule})\n`
        // }
        data += `\n\tdNdT = [\n`
        data += this.make_final_list()
        data += `\t]\n\n`
        data += `\treturn dNdT\n`
        data += '```\n---\n'
        return data
    }

    make_final_list() {

        const trim_this_line = (line) => line.trimEnd().replace(',', '')

        let data: string[] = []
        const modify_reaction = (name, reaction) => {
            const index = this.nameOfReactantsArr.indexOf(name)
            if(data[index]) {
                data[index] = trim_this_line(data[index]) + `${reaction}`
            } else {
                data[index] = `\t\t${reaction}`
            }
            data[index] += ',\n'
        }
        this.loss_channels.forEach(({ name, lossFrom, attachTo }) => {
            
            const loss_reaction = `(${name} * ${lossFrom})`
            modify_reaction(lossFrom, ` - ${loss_reaction}`)
            
            if (attachTo === 'none') return
            modify_reaction(attachTo, ` + ${loss_reaction}`)
        })

        data = data.map(trim_this_line).map((line, index) => {

            if(this.includeTrapLoss) {line += ` - (ktrap_loss * ${this.nameOfReactantsArr[index]})`}
            line += ',\n'
            return line
        })

        return data.join('')
    }

    get fullEquation() {
        try {
            
            return this.sliders + this.model
        } catch (error) {
            window.handleError(error)
            return null
        }
    }
}
