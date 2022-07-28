// import type { LossChannel } from 'types/types'

const baseRateConstant = -15
export const base_slider_values_str = (max='0.5') => `0, ${max}, 1e-3`
export const get_slider_controller = (n: number) => {
    const val = baseRateConstant*n
    return `1e${val - 3}, 1e${val + 3}, 1e${val - 4}`
}

export default function(
    nameOfReactantsArr: string[] = [], rateConstantMode: boolean = false, maxGuess:string
): Timescan.LossChannel[] {

    let defaultChannels: Timescan.LossChannel[] = []
    for (let i = 1; i < nameOfReactantsArr.length; i++) {

        const currention = nameOfReactantsArr[i - 1]
        const nextion = nameOfReactantsArr[i]

        const currentChannelForwards = {
            type: 'forwards',
            name: `k3${i}`,
            lossFrom: currention,
            attachTo: nextion,
            id: window.getID(),
            numberDensity: 'He^2',
            sliderController: rateConstantMode ? get_slider_controller(2) : base_slider_values_str(maxGuess),
        }

        const currentChannelBackwards = {
            type: 'backwards',
            name: `kCID${i}`,
            lossFrom: nextion,
            attachTo: currention,
            id: window.getID(),
            numberDensity: 'He^1',
            sliderController: rateConstantMode ? get_slider_controller(2) : base_slider_values_str(maxGuess),
        }
        defaultChannels = [...defaultChannels, currentChannelForwards, currentChannelBackwards]

    }
    return defaultChannels
}