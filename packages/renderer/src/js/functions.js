
import {mainPreModal} from "../svelteWritable";
import { writable } from 'svelte/store';
import { toast } from '@zerodevx/svelte-toast'
import {bulmaQuickview} from 'bulma-extensions';

export const activateChangelog = writable(false)
export const windowLoaded = writable(false);
export const updateAvailable = writable(false);
export const newVersion = writable("");
export const updating = writable(false);
export {plot, subplot} from "./plot"

import "./resizableDiv"
import "./clickOutside"
import "../Pages/general/computePy"





// window.createToast = (msg, type = "primary") => Toast.create({ message: msg, position: "is-top", type: `is-${type}` })
window.createToast = (msg, type = "primary") => {
    let theme = {};
    if(type==="danger") {
        theme =  {
            '--toastBackground': '#F56565',
            '--toastBarBackground': '#C53030'
        }
    } else if(type==="success") {
        theme = {
            '--toastBackground': '#48BB78',
            '--toastBarBackground': '#2F855A'
        }
    } else { theme = {} }

    toast.push(msg, {theme})

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

