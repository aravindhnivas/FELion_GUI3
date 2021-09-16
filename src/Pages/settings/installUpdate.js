
import { github, get } from "./svelteWritables";
import { updating } from "../../js/functions";
import { transferFiles } from "./backupAndRestore";
const {showMessageBoxSync} = dialogs
const restart_program = async () => {
    const response = await showMessageBoxSync({ title: "FELion_GUI3", type: "info", message: "Update succesfull", buttons: ["Restart", "Restart later"] })
    
    console.log("Restart: ", response)
    response === 0 ? reload() : console.log("Restarting later")

}

export function InstallUpdate(target, updateFolder) {

    let src = pathResolve(updateFolder, `${get(github).repo}-${get(github).branch}`)

    let dest = pathResolve(__dirname, "..")

    transferFiles({ dest, src })
        .then(() => {console.log("Copying downloaded files");})
        .catch((err) => { window.createToast("Error occured while copying downloaded files"); throw err; })
        .finally(() => { target.classList.toggle("is-loading"); updating.set(false); restart_program() })
}
// restart_program()