import type { loss_channelsType } from '$src/Pages/timescan/types/types'
export default function(nameOfReactantsArr: string[] = []): loss_channelsType[] {
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
        }

        const currentChannelBackwards = {
            type: 'backwards',
            name: `kCID${i}`,
            lossFrom: nextion,
            attachTo: currention,
            id: window.getID(),
            numberDensity: 'He^1',
        }
        defaultChannels = [...defaultChannels, currentChannelForwards, currentChannelBackwards]

    }
    return defaultChannels
}