<script>

    //  Importing
    import Layout from "../components/Layout.svelte"
    import CustomIconSwitch from "../components/CustomIconSwitch.svelte"
    import CustomSelect from "../components/CustomSelect.svelte"
    import CustomSwitch from "../components/CustomSwitch.svelte"

    import ReportLayout from "../components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import { fly, fade } from 'svelte/transition'
    import {plot, subplot} from "../js/functions.js"

    import {activated, modalContent} from "../components/Modal.svelte"
    import {createToast} from "../components/Layout.svelte"
    // import {afterUpdate} from "svelte"

    import {Icon} from '@smui/icon-button'
    /////////////////////////////////////////////////////////////////////////

    // Initialisation
    const filetype = "scan", id = "Timescan"
    let fileChecked = [];
    let currentLocation = localStorage[`${filetype}_location`] || ""
    $: scanfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    let openShell = false, graphPlotted = false
    let massIndex = 0, timestartIndex = 1, nshots = 10, power = "21, 21", resON_Files = "", resOFF_Files = ""

    let fullfiles = []
    $: if (currentLocation !== "") {
        fullfiles = ["", ...fs.readdirSync(currentLocation).filter(file=>file.endsWith("scan"))]
    }

    $: console.log(`ResOn: ${resON_Files}\nResOff: ${resOFF_Files}`)

    // Depletion Row
    let toggleRow = false
    let style = "width:7em; height:3.5em; margin-right:0.5em"

    // Linear log
    let logScale = false;

    function plotData({e=null, filetype="scan", tkplot="run"}={}){

        if (fileChecked.length === 0 && filetype === "scan") {return createToast("No files selected", "danger")}

        if (filetype === "general") {
            if (resOFF_Files === "" || resON_Files === "") {return createToast("No files selected", "danger")}
        }
        
        let pyfileInfo = {
            scan: {pyfile:"timescan.py" , args:[...scanfiles, tkplot]},
        
            general: {pyfile:"depletionscan.py" , args:[currentLocation,
                resON_Files, resOFF_Files, ...power.split(",").map(pow=>parseFloat(pow)), nshots, massIndex, timestartIndex]},
        }
        let {pyfile, args} = pyfileInfo[filetype]

        if (tkplot == "plot") {filetype = "general"}
        if (filetype == "general") {
            console.log("Sending general arguments: ", args)

            let py = spawn(

                localStorage["pythonpath"],
                [path.join(localStorage["pythonscript"], pyfile), args],
                
                { detached: true, stdio: 'ignore', shell: openShell }
            )
            py.on("close", ()=>{ console.log("Closed") })

            py.unref()
            py.ref()
            createToast("General process sent. Expect an response soon...")
            return;
            
        }

        let target = e.target

        target.classList.toggle("is-loading")
        if (filetype == "scan") {graphPlotted = false}

        let py;
        try {py = spawn( localStorage["pythonpath"], [path.resolve(localStorage["pythonscript"], pyfile), args] )}
        catch (err) {
            $modalContent = "Error accessing python. Set python location properly in Settings"
            $activated = true
            target.classList.toggle("is-loading")
            return
        }
        
        createToast("Process Started")
        py.stdout.on("data", data => {
            console.log("Ouput from python")
            let dataReceived = data.toString("utf8")
            console.log(dataReceived)
        });

        let error_occured_py = false

        py.stderr.on("data", err => {
            $modalContent = err
            $activated = true
            error_occured_py = true;
        });

        py.on("close", () => {
            if (!error_occured_py) {

                try {
                    let dataFromPython = fs.readFileSync(path.join(localStorage["pythonscript"], "data.json"))
                    dataFromPython = JSON.parse(dataFromPython.toString("utf-8"))
                    console.log(dataFromPython)
                    if (filetype=="scan") {
                       fileChecked.forEach(file=>{
                            plot(`Timescan Plot: ${file}`, "Time (in ms)", "Counts", dataFromPython[file], `${file}_tplot`)
                       })
                    } 

                    createToast("Graph plotted", "success")
                    graphPlotted = true

                } catch (err) { $modalContent = err; $activated = true }

            }
            console.log("Process closed")
            target.classList.toggle("is-loading")
        })
    }

    // Linearlog check
    const linearlogCheck = (event) => {
        let layout = { yaxis: { title: "Counts", type: logScale ? "log" : null } }
        if(graphPlotted) {

            fileChecked.forEach(file => {
                let tplot = file + "_tplot";
                Plotly.relayout(tplot, layout);
            })
        }
    };

</script>

<style>
    .timescan_buttonContainer {min-height: 5em;}
    .button {margin-right: 0.5em;}
    .buttonRow {margin-bottom: 1em!important; align-items: center;}

    * :global(.mdc-select__native-control option) {color: black}
    .active {display: flex!important;}
    .hide {display: none;}
    .align {display: flex; align-items: center;}

</style>

<Layout {filetype} {id} bind:currentLocation bind:fileChecked>

    <div class="timescan_buttonContainer" slot="buttonContainer">

        <div class="content align buttonRow">
            <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Timescan Plot</button>
            <button class="button is-link" on:click="{()=>{toggleRow = !toggleRow}}">Depletion Plot</button>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"scan", tkplot:"plot"})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomSwitch style="margin: 0 1em;" on:change={linearlogCheck} bind:selected={logScale} label="Log"/>
        </div>

        <div class="animated fadeIn hide buttonRow" class:active={toggleRow} >
            <CustomSelect style="width:12em; height:3.5em; margin-right:0.5em" bind:picked={resON_Files} label="ResOn" options={fullfiles}/>
            <CustomSelect style="width:12em; height:3.5em; margin-right:0.5em" bind:picked={resOFF_Files} label="ResOFF" options={fullfiles}/>
            <Textfield {style} bind:value={power} label="Power (ON, OFF)" />
            <Textfield type="number" {style} bind:value={nshots} label="FELIX Hz" />
            <Textfield type="number" {style} bind:value={massIndex} label="Mass Index" />
            <Textfield type="number" {style} bind:value={timestartIndex} label="Time Index" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"general"})}">Submit</button>
        </div>

    </div>

    <div style="margin-right: 1em;" slot="plotContainer">
        <div id="tplotContainer">
            {#each fileChecked as scanfile}
                <div id="{scanfile}_tplot" style="padding-bottom:1em" />
            {/each}
        </div>

        <div class="animated fadeIn hide" class:active={graphPlotted} style="flex-direction:column ">
            <ReportLayout bind:currentLocation id="scanreport", plotID={[`${fileChecked[0]}_tplot`]}/>
        </div>
    </div>
    
</Layout>