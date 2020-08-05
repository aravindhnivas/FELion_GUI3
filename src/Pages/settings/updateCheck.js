
import {versionJson, get} from "./svelteWritables";
function checkWithCurrentVersion({new_version, developer_version, info}={}) {
    if (window.currentVersion === new_version) {
        if (developer_version) {

                if (info) {window.createToast(`CAUTION! You are checking with developer branch which has experimental features. Take backup before updating.`, "danger")}
            } else { if (info) {window.createToast("No stable update available", "warning")}}
    
    } else if (window.currentVersion < new_version) {

        window.createToast("New update available", "success")

        let options = {
            title: "FELion_GUI3",
            message: "Update available "+new_version,
            buttons: ["Update and restart", "Later"],
            type:"info"
        }
        let response = window.showinfo(window.remote.getCurrentWindow(), options)
        response === 0 ? update() : window.createToast("Not updating now")
    }
}

export function updateCheck({info=true}={}){
    
    let target = document.getElementById("updateCheckBtn")

    target.classList.toggle("is-loading")

    if (!navigator.onLine) {if (info) {window.createToast("No Internet Connection!", "warning")}; return}

    console.log(`URL_Package: ${get(versionJson)}`)
    let developer_version = false

    let new_version = ""

    fetch(get(versionJson))

        .then(response => {
            if(response.ok) return response.json()
            throw new Error("URL Invalid")


        })

        .then(data => {
            console.log(`Received package:`, data)

            new_version = data.version
            developer_version = data.developer
            console.log(`Version available ${new_version}`)

            console.log(`Current version ${window.currentVersion}`)

            checkWithCurrentVersion({new_version, developer_version, info})
        })

        .catch(error=> window.createToast(error, "danger"))
        .finally(()=>{
            console.log("Update check completed")

            target.classList.toggle("is-loading")
        })
}