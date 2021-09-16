
import { github, get } from "./svelteWritables";
import { updating } from "../../js/functions";
import { transferFiles } from "./backupAndRestore";

const restart_program = () => {
    let response = window.showinfo({ title: "FELion_GUI3", type: "info", message: "Update succesfull", buttons: ["Restart", "Restart later"] })
    
    const mainWindowReload = window["electron-modules"]["reload"]
    response === 0 ? mainWindowReload() : console.log("Restarting later")

}

export function InstallUpdate(target, updateFolder) {

    let src = pathResolve(updateFolder, `${get(github).repo}-${get(github).branch}`)

    let dest = pathResolve(__dirname, "..")

    transferFiles({ dest, src })
        .then(() => {console.log("Copying downloaded files");})
        .catch((err) => { window.createToast("Error occured while copying downloaded files"); throw err; })
        .finally(() => { target.classList.toggle("is-loading"); updating.set(false); restart_program() })
}