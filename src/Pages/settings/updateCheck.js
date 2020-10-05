
import {versionJson, githubRepo, get} from "./svelteWritables";
import {activateChangelog, updateAvailable, newVersion} from "../../js/functions";

const updateEvent = new CustomEvent('update', { bubbles: false });

function checkWithCurrentVersion({new_version, developer_version, info}={}) {

    if (window.currentVersion === new_version) {
        if (developer_version) {
                if (info) {window.createToast(`CAUTION! You are checking with developer branch which has experimental features. Take backup before updating.`, "danger")}
            } else { if (info) {

                window.createToast("No stable update available", "warning");
                updateAvailable.set(false)
                window.changelogNewContent = ""

            }}
    
    } else if (window.currentVersion < new_version) {
        
        const changelogContentFile = get(githubRepo)+"/CHANGELOG.md"

        window.changelogNewContent = ""
        fetch(changelogContentFile)
            .then(response => response.text())
            .then(result => {
                window.changelogNewContent=result
                updateAvailable.set(true)
                activateChangelog.set(true)
                newVersion.set(new_version)
                console.log(window.changelogNewContent)
            })
            .catch(error=> window.createToast(error, "danger"))
            
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