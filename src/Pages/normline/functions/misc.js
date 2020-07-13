
// Importing modules
import {felixopoLocation, felixPeakTable, filedetails} from "./svelteWritables";
import { get } from 'svelte/store';
import { Toast } from 'svelma'

const createToast = (msg, type="primary") => Toast.create({ message: msg, position:"is-top", type:`is-${type}`})

export function savefile({file={}, name=""}={}) {

    let filename = path.join(get(felixopoLocation), `${name}.json`)
    fs.writeFile(filename, JSON.stringify({file}), 'utf8', function (err) {

        if (err) {
            console.log("An error occured while writing to File.");
            return createToast("An error occured while writing to File.", "danger")
        }
        return createToast(`${name}.json has been saved.`, "success");
    });
}


export function loadfile({name=""}={}) {
    let filename = path.join(get(felixopoLocation), `${name}.json`)
    if(!fs.existsSync(filename)) {return createToast(`${name}.json doesn't exist in DATA dir.`, "danger")}

    let loadedfile = JSON.parse(fs.readFileSync(filename)).file

    createToast(`${name}.json has been loaded.`, "success")
    return loadedfile
}