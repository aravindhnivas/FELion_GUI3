<script>

    // Importing modules
    import Textfield from '@smui/textfield';
    import {browse, createToast} from "../components/Layout.svelte"
    import {onMount} from "svelte"
    import CustomDialog from "../components/CustomDialog.svelte"

    import CustomSelect from '../components/CustomSelect.svelte';

    const {exec} = require("child_process")
    const https = require('https');

    const admZip = require('adm-zip');
    import {activated, modalContent} from "../components/Modal.svelte"
    const copy = require('recursive-copy')

    ///////////////////////////////////////////////////////

    let selected = "Configuration"

    let pythonpath = localStorage["pythonpath"] || path.resolve(__dirname, "../python3.7/python")

    let pythonscript = localStorage["pythonscript"] = path.resolve(__dirname, "assets/python_files")
    
    const navigate = (e) => {selected = e.target.innerHTML}

    function checkPython(){

        console.log("Python path checking \n", pythonpath)
        
        return new Promise((resolve, reject)=>{
            exec(`${pythonpath} -V`, (err, stdout, stderr)=>{err ? reject("Invalid") : resolve("Done")})
        })
    }

    const resetlocation = () => {
        
        checkPython()
        .then(res=>{
            pythonpath = localStorage["pythonpath"] = path.resolve(__dirname, "../python3.7/python")
            createToast("Location resetted", "warning")
        }).catch(err=>{ createToast("Default python location is not valid", "danger") } )
        pythonscript = localStorage["pythonscript"] = path.resolve(__dirname, "assets/python_files")
    }

    const savelocation = async () => {
        checkPython()
        .then(res=>{
            localStorage["pythonpath"] = pythonpath
            createToast("Location updated", "success")
        }).catch(err=>{ createToast("python location is not valid", "danger") })
        localStorage["pythonscript"] = pythonscript

    }

    let pythonpathCheck;
    onMount(()=>{
        checkPython()
        .then(res=>{ console.log("Python path is valid")})
        .catch(err=>pythonpathCheck.open() )
    })

    const handlepythonPathCheck = () => {
        console.log("Python path checking done")

    }

    // UPDATE

    let gihub_branchname =  "master", github_repo =  "FELion_GUI3", github_username =  "aravindhnivas"
    let versionFile = fs.readFileSync(path.join(__dirname, "../version.json"))

    let currentVersion = localStorage["version"] =  JSON.parse(versionFile.toString("utf-8")).version

    $: versionJson = `https://raw.githubusercontent.com/${github_username}/${github_repo}/${gihub_branchname}/version.json`
    $: urlzip = `https://codeload.github.com/${github_username}/${github_repo}/zip/${gihub_branchname}`

    const updateFolder = path.resolve(__dirname, "..", "update")
    const updatefilename = "update.zip"
    const zipFile = path.resolve(updateFolder, updatefilename)

    const updateCheck = () => {
        if (!navigator.onLine) {return createToast("No Internet Connection!", "warning")}
        
        // createToast("Checking for update", "warning")
        console.log(`URL_Package: ${versionJson}`)

        let developer_version = false

        console.log(`URL_ZIP: ${urlzip}`)
        let new_version = ""

        let request = https.get(versionJson, (res) => {

            console.log('statusCode:', res.statusCode);
            if (res.statusCode === 404) {return createToast("URL is not valid", "danger")}

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
            res.on("error", (err)=>{

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
                    createToast(`CAUTION! You are checking with developer branch which has experimental features. Take backup before updating.`, "danger")
                } else {createToast("No stable update available", "warning")}
            }


            else if (currentVersion < new_version) {

                createToast("New update available", "success")

                let options = {
                    title: "FELion_GUI3",
                    message: "Update available "+new_version,
                    buttons: ["Update and restart", "Later"],
                    type:"info"
                }
                
                let response = remote.dialog.showMessageBox(remote.getCurrentWindow(), options)
                console.log(response)
                switch (response) {
                    case 0:
                        update()
                    break;
                    case 1:
                        createToast("Not updating now")
                    break;
                }

            }
            console.log("Update check completed")
            // createToast("Update check completed", "success")

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

                let zip = new admZip(zipFile)

                zip.extractAllTo(updateFolder, /*overwrite*/true)
                // console.log("File Extracted")
                resolve("File extracted")
                createToast("Downloading Completed")

            })
        })
    }

    const update = async () => {

        if (!fs.existsSync(updateFolder)) {fs.mkdirSync(updateFolder)}

        await download()
        InstallUpdate()
    }


    const InstallUpdate = () => {

        console.log("Copying downloaded files")

        let src = path.resolve(updateFolder, `${github_repo}-${gihub_branchname}`)
        let dest = path.resolve(__dirname, "..")

        copy(src, dest, {overwrite: true}, function(error, results) {
            if (error) {
                console.error('Copy failed: ' + error);
                createToast("Update failed.\nMaybe the user doesn't have necessary persmission to write files in the disk", "danger")
            } else {
                console.info('Copied ' + results.length + ' files');
                createToast("Updated succesfull. Restart the program (Press Ctrl + R).", "success")
                let response = remote.dialog.showMessageBox(remote.getCurrentWindow(), 
                    {title:"FELion_GUI3", type:"info", message:"Update succesfull", buttons:["Restart", "Restart later"]}
                )
                if (response===0) {remote.getCurrentWindow().reload()}
            }
        })
    }

    // Backup and restore

    let backupName = "FELion_GUI_backup"
    let _src = {path:path.resolve(__dirname, "..", "src"), name:"src"}

    let _static = {path:path.resolve(__dirname, "..", "static"), name:"static"}
    let packageFile = {path:path.resolve(__dirname, "..", "package.json"), name:"package.json"}
    let versionFileJson = {path:path.resolve(__dirname, "..", "version.json"), name:"version.json"}
    let mainJs = {path:path.resolve(__dirname, "..", "main.js"), name:"main.js"}
    let rollup = {path:path.resolve(__dirname, "..", "rollup.config.js"), name:"rollup.config.js"}
    let svelteCongfig = {path:path.resolve(__dirname, "..", "svelte.config.js"), name:"svelte.config.js"}

    let folders = [_src, _static, packageFile, versionFileJson, mainJs, rollup, svelteCongfig]

    const backUp = (event) => {

        backupClass = "is-loading is-link"

        console.log(`Archiving existing software to ${backupName}.zip`)

        browse({dir:true})
        .then(result=>{

            let folderName;
            if (!result.canceled) {
                folderName = result.filePaths[0]
            } else {return console.log("Cancelled")}

            console.log("Selected folder: ", folderName)
            folders.forEach(folder=>{
                const _dest = path.resolve(folderName, backupName , folder.name)
                copy(folder.path, _dest, {overwrite: true}, function(error, results) {
                    if (error) { console.log('Copy failed: ' + error); createToast("Error Occured while copying", "danger")}
                    else {
                        console.info('Copied ' + results.length + ' files')
                        console.info('Copied ' + results + ' files')
                    }
                })
                
            })

            console.log("BackUp completed")

            createToast("BackUp completed", "success")
            
        })
        .catch(err=>{
            console.log(err)

            $modalContent = err
            $activated = true
        })
    }

    const restore = () =>{

        console.log(`Restoring existing software to ${__dirname}`)
        browse({dir:true})
        .then(result=>{

            let folderName;
            if (!result.canceled) { folderName = result.filePaths[0] } 
            else {return console.log("Cancelled")}

            console.log("Selected folder: ", folderName)

            folders.forEach(folder=>{
                const _dest = path.resolve(__dirname, "..", folder.name)
                copy(folder.path, _dest, {overwrite: true}, function(error, results) {
                    if (error) { console.log('Copy failed: ' + error); createToast("Error Occured while copying", "danger")} 
                    else {
                        console.info('Copied ' + results.length + ' files')
                        console.info('Copied ' + results + ' files')
                    }
                })
            })

            let response = remote.dialog.showMessageBox(remote.getCurrentWindow(),
                {title:"FELion_GUI3", type:"info", message:"Restored succesfull", buttons:["Restart", "Restart later"]} )
            if (response===0) remote.getCurrentWindow().reload()
            else console.log("Restarting later")

            console.log("Restoring completed")
            createToast("Restoring completed", "success")

        })

        .catch(err=>{

            console.log(err)
        
            $modalContent = err
            $activated = true

        })
    }
        

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

<CustomDialog id="pythonpath_Check" bind:dialog={pythonpathCheck} on:response={handlepythonPathCheck}
    title={"Python path is not valid"} content={"Change it in Settings --> Configuration"} label1="Okay", label2="Cancel"/>

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
                        <button class="button is-link" on:click={updateCheck}>Check update</button>
                        <button class="button is-link" on:click={update}>Update</button>
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