<script>

    // Importing modules
    import Textfield from '@smui/textfield';
    import {browse, createToast} from "../components/Layout.svelte"
    import {onMount} from "svelte"
    import CustomDialog from "../components/CustomDialog.svelte"

    import CustomSelect from '../components/CustomSelect.svelte';

    import PreModal from "../components/PreModal.svelte";


    const {exec} = require("child_process")
    const https = require('https');
    const admZip = require('adm-zip');

    const copy = require('recursive-copy')

    ///////////////////////////////////////////////////////

    // Electron version checking
    let electronVersion = process.versions.electron
    let showinfo = electronVersion >= "7" ? remote.dialog.showMessageBoxSync : remote.dialog.showMessageBox
    

    let selected = "Configuration", pyVersion = ""
    let pythonpath;
    if (process.platform === 'win32') {
        const currPath = path.resolve(__dirname, "../python3.7")
        if (fs.existsSync(currPath)) {
            const newPath = path.resolve(__dirname, "../python3")
            
            fs.rename(currPath, newPath, function(err) {

                if (err) { console.log(err) } else { 
                    if (localStorage["pythonpath"] === path.join(currPath, "python")) {pythonpath = localStorage["pythonpath"] = path.join(newPath, "python")}
                    console.log("Successfully renamed the directory.")
                 }
            })
        }

        if (!localStorage["pythonpath"]) {pythonpath = localStorage["pythonpath"] = path.resolve(__dirname, "../python3/python")}
        else {pythonpath = localStorage["pythonpath"] }
    } else { 
        if (!localStorage["pythonpath"]) {pythonpath = localStorage["pythonpath"] = path.resolve("/usr/local/bin/python")}
        else {pythonpath = localStorage["pythonpath"] }
     }

    
    
    let pythonscript = localStorage["pythonscript"] = path.resolve(__dirname, "assets/python_files")
    
    const navigate = (e) => {selected = e.target.innerHTML}

    function checkPython(){
        console.log("Python path checking \n", pythonpath)
        
        return new Promise((resolve, reject)=>{
            exec(`${pythonpath} -V`, (err, stdout)=>{err ? reject("Invalid") : resolve(stdout.trim())})
        })
    }

    const resetlocation = () => {
        let defaultPy = path.resolve(__dirname, "../python3/python")
        exec(`${defaultPy} -V`, (err, stdout)=>{
            if(err){createToast("Default python location is not valid", "danger") }
            else {pyVersion = stdout.trim(); pythonpath = localStorage["pythonpath"] = defaultPy; createToast("Location resetted", "warning")}
        })
        pythonscript = localStorage["pythonscript"] = path.resolve(__dirname, "assets/python_files")

    }

    const savelocation = async () => {
        checkPython().then(res=>{

            pyVersion = res
            localStorage["pythonpath"] = pythonpath
            createToast("Location updated", "success")
        }).catch(()=>{ createToast("python location is not valid", "danger") })
        localStorage["pythonscript"] = pythonscript
    }
    let pythonpathCheck;

    // let update_checking;
    onMount(()=>{
        setTimeout(()=>{checkPython().then(res=>{ pyVersion = res; console.log("Python path is valid")}).catch(()=>pythonpathCheck.open() )}, 1000)

        updateCheck({info:false})
        // update_checking = setInterval(()=>{updateCheck({info:false})}, 1*1000*60*15)
        setInterval(()=>{updateCheck({info:false})}, 1*1000*60*15)
    })

    const handlepythonPathCheck = () => { console.log("Python path checking done") }

    // UPDATE
    let gihub_branchname =  "master", github_repo =  "FELion_GUI3", github_username =  "aravindhnivas"
    let versionFile = fs.readFileSync(path.join(__dirname, "../version.json"))

    let currentVersion = localStorage["version"] =  JSON.parse(versionFile.toString("utf-8")).version


    $: versionJson = `https://raw.githubusercontent.com/${github_username}/${github_repo}/${gihub_branchname}/version.json`
    $: urlzip = `https://codeload.github.com/${github_username}/${github_repo}/zip/${gihub_branchname}`

    const updateFolder = path.resolve(__dirname, "..", "update")
    const updatefilename = "update.zip"
    const zipFile = path.resolve(updateFolder, updatefilename)

    const updateCheck = ({info=true}={}) => {

        let target = document.getElementById("updateCheckBtn")

        target.classList.toggle("is-loading")

        if (!navigator.onLine) {if (info) {createToast("No Internet Connection!", "warning")}; return}

        console.log(`URL_Package: ${versionJson}`)
        let developer_version = false

        console.log(`URL_ZIP: ${urlzip}`)
        let new_version = ""

        let request = https.get(versionJson, (res) => {

            console.log('statusCode:', res.statusCode);
            if (res.statusCode === 404) { if (info) {createToast("URL is not valid", "danger")}; return}
            console.log('headers:', res.headers);
            res.on('data', (data) => {
                data = data.toString("utf8")
                console.log(data)
                data = JSON.parse(data)
                console.log(data)
                new_version = data.version
                developer_version = data.developer

                console.log(`Developer version: ${developer_version}`)
                console.log(`Received package:`, data)

                console.log(`Version available ${new_version}`)
                console.log(`Current version ${currentVersion}`)

            })

            res.on("error", ()=>{
                console.log("Error while reading downloaded data: ")
                new_version = ""
            })

            res.on("close", ()=>{console.log("Update request completed.")})

        })

        request.on('error', (err) => {
            console.log("Error occured: (Try again or maybe check your internet connection)\n", err)
        })

        request.on("close", ()=>{

            if (currentVersion === new_version) {
                if (developer_version) {
                    if (info) {createToast(`CAUTION! You are checking with developer branch which has experimental features. Take backup before updating.`, "danger")}
                } else { if (info) {createToast("No stable update available", "warning")}}
            }


            else if (currentVersion < new_version) {

                createToast("New update available", "success")

                let options = {
                    title: "FELion_GUI3",
                    message: "Update available "+new_version,
                    buttons: ["Update and restart", "Later"],
                    type:"info"
                }
                let response = showinfo(remote.getCurrentWindow(), options)
                response === 0 ? update() : createToast("Not updating now")

            }
            console.log("Update check completed")
            target.classList.toggle("is-loading")
        })

    }

    // Download the update file
    const download = () => {

        // const downloadedFile = fs.createWriteStream(zipFile)
        return new Promise((resolve)=>{

            let response = https.get(urlzip, (res) => {
                console.log(`URL: ${urlzip}`)
                console.log('statusCode:', res.statusCode);

                console.log('headers:', res.headers);

                res.pipe(fs.createWriteStream(zipFile))
                console.log("File downloaded")

            })

            response.on("close", () => {
                
                console.log("Downloading Completed")
                console.log("Extracting files")

                setTimeout(()=>{

                    let zip = new admZip(zipFile);
                    zip.extractAllTo(updateFolder, /*overwrite*/true);
                    console.log("File Extracted")

                    resolve("File extracted")
                    createToast("Downloading Completed")
                }, 1600)
            })
        })
    }

    const update = async () => {

        let target = document.getElementById("updateBtn")

        target.classList.toggle("is-loading")

        if (!fs.existsSync(updateFolder)) {fs.mkdirSync(updateFolder)}
        
        await download()
        InstallUpdate(target)
    }

    const restart_program = () => {
        let response = showinfo(remote.getCurrentWindow(), {title:"FELion_GUI3", type:"info", message:"Update succesfull", buttons:["Restart", "Restart later"]} )

        response===0 ? remote.getCurrentWindow().reload() : console.log("Restarting later")
    }

    const InstallUpdate = (target) => {

        console.log("Copying downloaded files")

        let src = path.resolve(updateFolder, `${github_repo}-${gihub_branchname}`)
        let dest = path.resolve(__dirname, "..")

        copy(src, dest, {overwrite: true}, function(error, results) {
            if (error) {
                console.error('Copy failed: ' + error);
                createToast("Update failed.\nMaybe the user doesn't have necessary persmission to write files in the disk", "danger")

                return target.classList.toggle("is-loading")
            } else {
                console.info('Copied ' + results.length + ' files')

                createToast("Updated succesfull. Restart the program (Press Ctrl + R).", "success")
                target.classList.toggle("is-loading")

                restart_program()

            }
        })
    }

    // Backup and restore
    let backupName = "FELion_GUI_backup"
    const backUp = (event) => {

        let target = event.target
        
        browse({dir:true}).then(result=>{

            let folderName;
            if (!result.canceled) { folderName = result.filePaths[0] } else {return console.log("Cancelled")}

            target.classList.toggle("is-loading")
            console.log("Selected folder: ", folderName)

            const _dest = path.resolve(folderName, backupName)
            const _src =path.resolve(__dirname, "..")

            copy(_src, _dest, {overwrite: true, filter:fs.readdirSync(_src).filter(file => file != "node_modules")}, function(error, results) {
                if (error) { console.log('Copy failed: ' + error); createToast("Error Occured while copying", "danger"); target.classList.toggle("is-loading")}
            
                else {
                    console.info('Copied ' + results.length + ' files')
                    console.log("BackUp completed")
                    createToast("BackUp completed", "success")
                    target.classList.toggle("is-loading")
                }
            })
        })
        .catch(err=>{
            console.log(err)
            preModal.modalContent = err
            preModal.open = true
        })
    }

    const restore = () =>{
        console.log(`Restoring existing software to ${__dirname}`)

        let target = event.target
        browse({dir:true}).then(result=>{

            let folderName;
            if (!result.canceled) { folderName = result.filePaths[0] } else {return console.log("Cancelled")}

            target.classList.toggle("is-loading")
            console.log("Selected folder: ", folderName)

            const _dest = path.resolve(__dirname, "..")
            const _src = path.resolve(folderName, backupName)
            
            copy(_src, _dest, {overwrite: true}, function(error, results) {
                if (error) { console.log('Copy failed: ' + error); createToast("Error Occured while copying", "danger"); target.classList.toggle("is-loading")}
                else {
                    console.info('Copied ' + results.length + ' files')
                    target.classList.toggle("is-loading")


                    restart_program()
                    console.log("Restoring completed")
                    createToast("Restoring completed", "success")
                }

            })
        })
        .catch(err=>{
            console.log(err)
            preModal.modalContent = err
            preModal.open = true
        })


    }
    let preModal = {};
</script>

<style>

    section { margin: 0; padding: 0; }
    .side-panel, .main-panel {height: calc(100vh - 7em);}
    .box { background-color: #6a50ad8a}
    .main-panel {margin: 0 5em;}

    .left .title { letter-spacing: 0.1em; text-transform: uppercase; padding: 0.5em;
        font-size: larger; cursor: pointer; border-radius: 20px 0; margin-bottom: 1em;
    }

    .container {padding: 2em; display: grid;}
    .clicked {border-left: 2px solid #fafafa; background-color: #6a50ad;}
    .right > div {display: none;}
    .active {display: block!important; }
    .right .title {letter-spacing: 0.1em; text-transform: uppercase;}
    
    * :global(option) { color: black; }

</style>
<PreModal bind:preModal />
<CustomDialog id="pythonpath_Check" bind:dialog={pythonpathCheck} on:response={handlepythonPathCheck}
    title={"Python path is not valid"} content={"Change it in Settings --> Configuration"} label1="Okay" label2="Cancel" />

<section class="section animated fadeIn" id="Settings" style="display:none">
    <div class="columns">

        <div class="column side-panel is-2-widescreen is-3-desktop is-4-tablet box adjust-right">
            <div class="container left">
                <div class="title nav hvr-glow" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="title nav hvr-glow" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="title nav hvr-glow" class:clicked={selected==="About"} on:click={navigate}>About</div>
            </div>
        </div>

        <div class="column main-panel box">
            <div class="container right">

                <!-- Configuration -->
                <div class="content animated fadeIn" class:active={selected==="Configuration"}>
                    <h1 class="title">Configuration</h1>
                    <div class="subtitle">{pyVersion}</div>
                    <Textfield style="margin-bottom:1em;" bind:value={pythonpath} label="Python path" />
                    <Textfield style="margin-bottom:1em;" bind:value={pythonscript} label="Python script path" />
                    
                    <button class="button is-link" on:click={resetlocation}>Reset</button>
                    <button class="button is-link" on:click={savelocation}>Save</button>

                </div>

                <!-- Update -->
                <div class="content animated fadeIn" class:active={selected==="Update"}>
                    <h1 class="title">Update</h1>
                    <div class="subtitle">Current Version {currentVersion}</div>
                    
                    <div class="content">
                        <Textfield style="width:7em; margin-right:2em;" bind:value={github_username} label="Github username" />
                        <Textfield style="width:7em; margin-right:2em;" bind:value={github_repo} label="Github Repo" />
                        <CustomSelect bind:picked={gihub_branchname} label="Github branch" options={["master", "developer"]}/>
                    </div>

                    <div class="content">
                        <button class="button is-link" id="updateCheckBtn" on:click={updateCheck}>Check update</button>
                        <button class="button is-link" id="updateBtn" on:click={update}>Update</button>
                    </div>


                    <div class="content">
                        <Textfield style="width:30%; margin-right:2em;" bind:value={backupName} label="Github username" />
                        <button class="button is-link" on:click={backUp}>Backup</button>
                        <button class="button is-link" on:click={restore}>Restore</button>
                    </div>
                    

                </div>

                <!-- About -->
                <div class="content animated fadeIn" class:active={selected==="About"}>
                    <h1 class="title">About</h1>

                </div>
                
            </div>
        </div>

    </div>
    
</section>