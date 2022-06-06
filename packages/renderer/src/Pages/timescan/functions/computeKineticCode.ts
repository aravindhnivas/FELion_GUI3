
import type { loss_channelsType } from '$src/Pages/timescan/types/types'
export interface ComputeKineticCodeType {
    nameOfReactants: string;
    ratek3: string;
    ratekCID: string;
    k3Guess: string;
    kCIDGuess: string;
    loss_channels: loss_channelsType[];
    // includeTrapLoss: boolean;
    rateConstantMode: boolean
}

export class computeKineticCodeScipy {

    nameOfReactants: string
    ratek3: string
    ratekCID: string
    k3Guess: string
    kCIDGuess: string
    loss_channels: loss_channelsType[]
    sliderControlls: {forwards: string[], backwards: string[]} = {forwards: [], backwards: []}
    nameOfReactantsArr: string[]
    rateForwardArr: string[]
    rateReverseArr: string[]
    rateConstantMode: boolean;

    constructor(maindata: ComputeKineticCodeType) {

        this.nameOfReactants = maindata.nameOfReactants
        this.ratek3 = maindata.ratek3
        this.ratekCID = maindata.ratekCID
        this.k3Guess = maindata.k3Guess
        this.kCIDGuess = maindata.kCIDGuess
        this.loss_channels = maindata.loss_channels
        // this.includeTrapLoss = maindata.includeTrapLoss
        this.rateConstantMode = maindata.rateConstantMode

        this.nameOfReactantsArr = this.nameOfReactants.split(',').map((name) => name.trim())

        const forwardChannels = this.loss_channels.filter(({ type }) => type === 'forwards')
        const backwardChannels = this.loss_channels.filter(({ type }) => type === 'backwards')

        this.sliderControlls.forwards = forwardChannels.map(({ sliderController }) => sliderController)
        this.rateForwardArr = [...forwardChannels.map(({ name }) => name)]
        
        this.sliderControlls.backwards = backwardChannels.map(({ sliderController }) => sliderController)
        this.rateReverseArr = [...backwardChannels.map(({ name }) => name)]

    }

    get sliders() {
        let data = ''
        data += '## Defining min-max-value for sliders\n'
        data += '```plaintext\n'
        data += '\nmin_max_step_controller = {}\n'
        data += '\nmin_max_step_controller["forwards"] = {\n'
        this.rateForwardArr.forEach((value, index) => {
            // data += `\t'${value}': (${this.k3Guess}),\n`
            data += `\t'${value}': (${this.sliderControlls.forwards[index]}),\n`
        })
        
        data += '}\n'
        data += '\nmin_max_step_controller["backwards"] = {\n'

        this.rateReverseArr.forEach((value, index) => {
            // data += `\t'${value}': (${this.kCIDGuess}),\n`
            data += `\t'${value}': (${this.sliderControlls.backwards[index]}),\n`
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
        
        if(this.rateForwardArr.length > 0) {
            data += `\t${this.rateForwardArr.join(', ')}${this.rateForwardArr.length == 1 ? ',' : ''}  = k3\n`
        }

        if(this.rateReverseArr.length > 0) {
            data += `\t${this.rateReverseArr.join(', ')}${this.rateReverseArr.length == 1 ? ',' : ''} = kCID\n\n`
        }
        data += `\t${this.nameOfReactantsArr.join(', ')} = N\n`
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
            if (data[index]) {
                data[index] = trim_this_line(data[index]) + `${reaction}`
            } else {
                data[index] = `\t\t${reaction}`
            }
            data[index] += ',\n'
        }

        let attach_to_all_lists = []
        this.loss_channels.forEach((channel) => {
            const { name, lossFrom, attachTo, numberDensity } = channel
            
            if (lossFrom === '<resp. ion>') {
                return
            }
            
            let loss_reaction;
            if(this.rateConstantMode && numberDensity) {
                loss_reaction = `(${name} * ${numberDensity.replace('^1', '').replace('^', '**')} * ${lossFrom})`
            } else {
                loss_reaction = `(${name} * ${lossFrom})`
            }
            modify_reaction(lossFrom, ` - ${loss_reaction}`)

            if (attachTo === 'none') return
            if (attachTo === 'all') {
                attach_to_all_lists.push({lossFrom, loss_reaction})
                return
            }
            modify_reaction(attachTo, ` + ${loss_reaction}`)
        })
        console.log(attach_to_all_lists)
        attach_to_all_lists.forEach(({lossFrom, loss_reaction}) => {
            const fromIndex = this.nameOfReactantsArr.indexOf(lossFrom)
            data = data.map((name, index) => {
                if (index === fromIndex) return name
                return `${trim_this_line(name)} + ${loss_reaction},\n`
            })
        })

        console.log(data)

        const channels_to_add_in_all_ions = this.loss_channels.filter(channel=>channel.lossFrom === '<resp. ion>')
        channels_to_add_in_all_ions.forEach((channel) => {
            data = data.map(trim_this_line).map((line, index) => {
                line += ` - (${channel.name}  * ${this.nameOfReactantsArr[index]}),\n`
                return line
            })
        })
        return data.join('')
    }

    get fullEquation(): string {

        try {
            return this.sliders + this.model
            
        } catch (error) {
            window.handleError(error)
            return ''
        }
    }
}
