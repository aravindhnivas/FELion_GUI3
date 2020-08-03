
import { writable } from 'svelte/store';
import { Toast } from 'svelma';

export const windowLoaded = writable(false);

window.addEventListener('DOMContentLoaded', (event) => {

    console.log('DOM fully loaded and parsed');
    windowLoaded.set(true)
});


export function resizableDiv({ div, change = { width: true, height: true }, cursor = { left: false, right: false, bottom: false, top: false } } = {}) {

    interact(div).resizable({

        edges: cursor,

        modifiers: [
            // keep the edges inside the parent
            interact.modifiers.restrictEdges({ outer: 'parent' }),
            interact.modifiers.restrictSize({ min: { width: 50, height: 50 }, max: { width: 500 } })
        ],
        inertia: true
    }).on('resizemove', function (event) {
        let target = event.target
        let x = (parseFloat(target.getAttribute('data-x')) || 0)
        let y = (parseFloat(target.getAttribute('data-y')) || 0)

        if (change.width) {
            target.style.width = event.rect.width + 'px'
            if (event.rect.width <= 50) {
                if (target.classList.contains("filebrowser")) { target.style.display = "none" }

            }
        
        }

        if (change.height) target.style.height = event.rect.height + 'px'

        // translate when resizing from top or left edges
        
        
        x += event.deltaRect.left
        
        y += event.deltaRect.top


        target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)'
        target.setAttribute('data-x', x)
        target.setAttribute('data-y', y)

    })

}
resizableDiv({ div: ".adjust-right", cursor: { right: true }, change: { width: true, height: false } })

export function plot(mainTitle, xtitle, ytitle, data, plotArea, filetype = null) {

    let dataLayout = {
        title: mainTitle,
        xaxis: { title: xtitle },
        yaxis: { title: ytitle },
        hovermode: 'closest',
        autosize: true,
        height: 450,
    }

    if (filetype == 'mass') { dataLayout.yaxis.type = "log" }
    
    let dataPlot = [];

    for (let x in data) { dataPlot.push(data[x]) }
    
    try { Plotly.react(plotArea, dataPlot, dataLayout, { editable: true }) } catch (err) { console.log("Error occured while plotting\n", err) }
}

export function subplot(mainTitle, xtitle, ytitle, data, plotArea, x2, y2, data2) {

    let dataLayout = {
        title: mainTitle,
        xaxis: { domain: [0, 0.4], title: xtitle },
        yaxis: { title: ytitle },
        xaxis2: { domain: [0.5, 1], title: x2 },
        yaxis2: { anchor: "x2", title: y2, overlaying: 'y', },

        yaxis3: { anchor: 'free', overlaying: 'y', side: 'right', title: "Measured (mJ)", position: 0.97 },
        autosize: true,
        height: 450,
    
    }

    let dataPlot1 = [];
    for (let x in data) { dataPlot1.push(data[x]) }
    let dataPlot2 = [];
    for (let x in data2) { dataPlot2.push(data2[x]) }
    Plotly.react(plotArea, dataPlot1.concat(dataPlot2), dataLayout, { editable: true })
}


// Global variables

window.electron = require("electron")
window.remote = electron.remote
window.path = require("path")
window.fs = require("fs")
window.spawn = require("child_process").spawn

window.createToast = (msg, type="primary") => Toast.create({ message: msg, position:"is-top", type:`is-${type}`})
window.sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));
window.targetElement = (id) => document.getElementById(id)

window.getPageStatus = (id) => targetElement(id).style.display !== "none"
window.showpage = (id) => { targetElement(id).style.display = "block" }

window.hidepage = (id) => { targetElement(id).style.display = "none" }

window.togglepage = (id) => {
    window.getPageStatus(id) ? targetElement(id).style.display = "none" : targetElement(id).style.display = "block"
}

const electronVersion = process.versions.electron
window.showinfo = electronVersion >= "7" ? remote.dialog.showMessageBoxSync : remote.dialog.showMessageBox

// Checking curernt version

const versionFile = fs.readFileSync(path.join(__dirname, "../version.json"))
window.currentVersion = localStorage["version"] =  JSON.parse(versionFile.toString("utf-8")).version





window.asyncForEach = async (array, callback) => {
    for (let index = 0; index < array.length; index++) {
        await callback(array[index], index, array);
    }

}