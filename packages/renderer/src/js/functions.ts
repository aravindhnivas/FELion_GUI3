import { mainPreModal } from '$src/sveltewritables'
import { writable } from 'svelte/store'
import { toast } from '@zerodevx/svelte-toast'
import bulmaQuickview from 'bulma-extensions/bulma-quickview/src/js/index.js'
// import './resizableDiv'
// import '../Pages/general/computePy'
export const activateChangelog = writable(false)
export const windowLoaded = writable(false)
export const updateAvailable = writable(false)
export const newVersion = writable('')
export const updating = writable(false)
export { plot, subplot, plotlyClick, plotlyEventsInfo } from './plot'

const toastTheme = {
    info: {},
    success: {
        '--toastBackground': '#48BB78',
        '--toastBarBackground': '#2F855A',
    },
    danger: {
        '--toastBackground': '#F56565',
        '--toastBarBackground': '#C53030',
    },
    warning: {
        '--toastBackground': '#FFB84D',
        '--toastBarBackground': '#C28B00',
    },
}

window.createToast = (description, type = 'info', opts = {}) => {
    toast.push(description, {
        theme: toastTheme[type],
        pausable: true,
        ...opts,
    })
}

window.sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

window.handleError = (error) => {
    console.error(error)
    if(typeof error === 'string') {
        mainPreModal.error(error)
    } else {
        mainPreModal.error(error.stack)
    }
}


window.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed')
    windowLoaded.set(true)
    bulmaQuickview.attach()

})

window.getID = () => Math.random().toString(32).substring(2)

window.clickOutside = (node) => {
    console.log(node)

    const handleClick = (event: ButtonClickEvent) => {
        if (node && !node.contains(event.target) && !event.defaultPrevented) {
            node.dispatchEvent(new CustomEvent('click_outside', {detail: event}))
        }
    }

    document.addEventListener('click', handleClick, true)
    return {
        destroy() {
            document.removeEventListener('click', handleClick, true)
        },
    }
}
