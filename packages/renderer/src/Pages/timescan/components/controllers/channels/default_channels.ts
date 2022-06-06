import type { loss_channelsType } from '$src/Pages/timescan/types/types'
export default function(nameOfReactantsArr: string[] = [], rateConstantMode: boolean = false): loss_channelsType[] {
    console.log('making default channels')
    let defaultChannels: loss_channelsType[] = []
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
            sliderController: rateConstantMode ? '1e-33, 1e-28, 1e-34' : '0, 0.5, 1e-3',
        }

        const currentChannelBackwards = {
            type: 'backwards',
            name: `kCID${i}`,
            lossFrom: nextion,
            attachTo: currention,
            id: window.getID(),
            numberDensity: 'He^1',
            sliderController: rateConstantMode ? '1e-17, 1e-14, 1e-18' : '0, 0.5, 1e-3',
        }
        defaultChannels = [...defaultChannels, currentChannelForwards, currentChannelBackwards]

    }
    return defaultChannels
}