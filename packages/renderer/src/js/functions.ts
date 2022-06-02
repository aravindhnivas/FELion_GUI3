import { mainPreModal } from '../svelteWritable'
import { writable } from 'svelte/store'
import { toast } from '@zerodevx/svelte-toast'
import type { SvelteToastOptions } from '@zerodevx/svelte-toast'
import bulmaQuickview from 'bulma-extensions/bulma-quickview/src/js/index.js'

export const activateChangelog = writable(false)
export const windowLoaded = writable(false)
export const updateAvailable = writable(false)
export const newVersion = writable('')
export const updating = writable(false)
export { plot, subplot, plotlyClick, plotlyEventsInfo } from './plot'

import './resizableDiv'
// import './clickOutside'
import '../Pages/general/computePy'

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
    mainPreModal.error(error.stack)
}


window.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed')
    windowLoaded.set(true)
    bulmaQuickview.attach()

})

window.getID = () => Math.random().toString(32).substring(2)

window.clickOutside = (node) => {
    
    console.log(node)

    const handleClick = (event) => {
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


/* eslint-disable @typescript-eslint/consistent-type-imports */
interface Exposed {

    createToast: (description: string, type?: 'info' | 'danger' | 'warning' | 'success', opts?: SvelteToastOptions) => void; 
    sleep: (ms: number) => Promise<typeof setTimeout>;
    handleError: (error: Error) => void;
    getID: () => string;
    clickOutside: (node: HTMLElement) => { destroy: () => void };
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
declare global {
    interface Window extends Exposed {}
}
