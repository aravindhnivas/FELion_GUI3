
import {mainPreModal} from "../svelteWritable";
import { writable } from 'svelte/store';
// import { toasts }  from "svelte-toasts";
import { toast } from '@zerodevx/svelte-toast'
import {bulmaQuickview} from 'bulma-extensions';

export const activateChangelog = writable(false)
export const windowLoaded = writable(false);
export const updateAvailable = writable(false);
export const newVersion = writable("");
export const updating = writable(false);
export {plot, subplot, plotlyClick, plotlyEventsInfo} from "./plot"

import "./resizableDiv"
import "./clickOutside"
import "../Pages/general/computePy"

const toastTheme = {
    info: {},
    success: {
        '--toastBackground': '#48BB78',
        '--toastBarBackground': '#2F855A'
    },
    danger: {
        '--toastBackground': '#F56565',
        '--toastBarBackground': '#C53030'
    },
    warning: {
        '--toastBackground': '#FFB84D',
        '--toastBarBackground': '#C28B00'
    }
}
window.createToast = (description, type = "info", opts={}) => {
    // const theme = {
    //     // title: type == 'danger' ? 'ERROR' : type.toUpperCase(),
    //     description,
    //     duration: 3000,
    //     placement,
	//     showProgress: false,
    //     type: type == 'danger' ? 'error' : type,
    //     theme: 'dark'
    // };
    // toasts.add(theme)
    toast.push(description, {theme: toastTheme[type], pausable: true, ...opts})
}
window.sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

window.handleError = (error) => {
    console.error(error)
    mainPreModal.error(error.stack || error )
    return
}

window.onerror = function (message, source, lineno, colno, error) {
    const modalContent =  `${error.name}: ${message}\nsource: ${source}\nlineno: ${lineno}\tcolno: ${colno}`
    window.handleError(modalContent)
};

window.targetElement = (id) => document.getElementById(id)
window.getPageStatus = (id) => targetElement(id).style.display !== "none"
window.showpage = (id) => { targetElement(id).style.display = "block" }
window.hidepage = (id) => { targetElement(id).style.display = "none" }
window.togglepage = (id) => {
    getPageStatus(id) ? targetElement(id).style.display = "none" : targetElement(id).style.display = "block"
}

window.asyncForEach = async (array, callback) => {
    for (let index = 0; index < array.length; index++) {await callback(array[index], index, array);}
}

window.addEventListener('DOMContentLoaded', (event) => {
    console.log('DOM fully loaded and parsed');
    windowLoaded.set(true)
    bulmaQuickview.attach()
});

