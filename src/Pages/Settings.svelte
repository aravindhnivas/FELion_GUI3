<script>

    // Importing modules
    import Textfield from '@smui/textfield';
    import {createToast} from "../components/Layout.svelte"
    import {onMount} from "svelte"
    import CustomDialog from "../components/CustomDialog.svelte"

    ///////////////////////////////////////////////////////

    let selected = "Configuration"
    let pythonpath = localStorage["pythonpath"] || path.resolve(__dirname, "../python3.7/python")
    let pythonscript = localStorage["pythonscript"] || path.resolve(__dirname, "assets/python_files")
    const navigate = (e) => {selected = e.target.innerHTML}

    const {exec} = require("child_process")

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

        console.log("Python path checking")
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
                    <div class="subtitle">Current Version {localStorage.version}</div>
                </div>

                <!-- About -->
                <div class="content animated fadeIn" class:active={selected==="About"}>
                    <h1 class="title">About</h1>

                </div>
                
            </div>
        </div>

    </div>
</section>