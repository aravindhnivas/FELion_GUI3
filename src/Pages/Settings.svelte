<script>

    // Importing modules
    import Textfield from '@smui/textfield';
    import {createToast} from "../components/Layout.svelte"
    import {onMount} from "svelte"
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

    onMount(()=>{
        checkPython()
        .then(res=>{ console.log("Python path is valid")})
        .catch(err=>window.alert("Set python path is not valid. Change it in Settings --> Configuration") )

    })
    
</script>

<style>

    section { margin: 0; padding: 0; }
    .side-panel, .main-panel {height: calc(100vh - 7em);}
    .box { background-color: #6a50ad8a}
    .main-panel {margin: 0 5em;}
    .left .title {
        letter-spacing: 0.1em; text-transform: uppercase; padding: 0.5em;
        font-size: larger; cursor: pointer;
    }

    .container {padding: 2em}
    .clicked {border-left: 2px solid #fafafa; background-color: #6a50ad; border-radius: 20px 0;}
    .right > div {display: none;}
    .active {display: block!important; }

</style>

<section class="section animated fadeIn" id="Settings" style="display:none">
    <div class="columns">
        <div class="column side-panel is-2-widescreen is-3-desktop is-4-tablet box adjust-right">
        
            <div class="container left">
                <div class="title nav" class:clicked={selected==="Configuration"} on:click={navigate}>Configuration</div>
                <div class="title nav" class:clicked={selected==="Update"} on:click={navigate}>Update</div>
                <div class="title nav" class:clicked={selected==="About"} on:click={navigate}>About</div>
            </div>

        </div>

        <div class="column main-panel box">
            <div class="container right">

                <!-- Configuration -->
                <div class="content animated fadeIn" class:active={selected==="Configuration"} id="Configuration">
                    <h1 class="title">Configuration</h1>
                    <hr>
                    <Textfield style="margin-bottom:1em;" bind:value={pythonpath} label="Python path" />
                    <Textfield style="margin-bottom:1em;" bind:value={pythonscript} label="Python script path" />
                    <button class="button is-link" on:click={resetlocation}>Reset</button>
                    <button class="button is-link" on:click={savelocation}>Save</button>

                </div>

                <!-- Update -->
                <div class="animated fadeIn" class:active={selected==="Update"} id="Configuration">
                    <h1 class="title">Update</h1>
                    <hr>

                </div>

                <!-- About -->
                <div class="animated fadeIn" class:active={selected==="About"} id="Configuration">
                    <h1 class="title">About</h1>
                    <hr>

                </div>
            </div>
        </div>
    </div>
</section>