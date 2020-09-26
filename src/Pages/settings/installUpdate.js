
import { github, get } from "./svelteWritables";
import { transferFiles } from "./backupAndRestore";

const restart_program = () => {
    let response = window.showinfo(remote.getCurrentWindow(), { title: "FELion_GUI3", type: "info", message: "Update succesfull", buttons: ["Restart", "Restart later"] })
    response === 0 ? remote.getCurrentWindow().reload() : console.log("Restarting later")

}

export function InstallUpdate(target, updateFolder) {
    let src = path.resolve(updateFolder, `${get(github).repo}-${get(github).branch}`)

    let dest = path.resolve(__dirname, "..")

    transferFiles({ dest, src })

        .then(() => {console.log("Copying downloaded files"); localStorage.showUpdate = "true"})

        .catch((err) => { window.createToast("Error occured while copying downloaded files"); throw err; })
        .finally(() => { target.classList.toggle("is-loading"); restart_program() })
}