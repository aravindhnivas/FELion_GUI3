
<script>
    import Textfield        from '@smui/textfield'
    import Layout           from "$components/Layout.svelte"
    import CustomIconSwitch from "$components/CustomIconSwitch.svelte"
    import CustomSelect     from "$components/CustomSelect.svelte"
    import CustomSwitch     from "$components/CustomSwitch.svelte"
    import ROSAAkinetics    from "../Pages/timescan/components/ROSAAkinetics.svelte"
    import {plot}           from "../js/functions.js"
    import {relayout}       from 'plotly.js/dist/plotly-basic';
    import {cloneDeep}      from "lodash-es"
    import computePy_func   from "$src/Pages/general/computePy"

    /////////////////////////////////////////////////////////////////////////

    // Initialisation

    const filetype = "scan"
    const id = "Timescan"

    let fileChecked = [];
    let currentLocation = ""
    $: scanfiles = fileChecked.map(file=>pathResolve(currentLocation, file))

    let nshots = 10
    let power = "21, 21"
    let openShell = false
    let massIndex = 0
    let fullfiles = []
    let resON_Files = ""
    let graphPlotted = false
    let resOFF_Files = "";
    let timestartIndex = 1
    let timestartIndexScan = 0;

    function dir_changed() {
        if (fs.existsSync(currentLocation)) {
            fullfiles = fs.readdirSync(currentLocation).filter(file=>file.endsWith(".scan"))
        }
    }

    $: console.log(`ResOn: ${resON_Files}\nResOff: ${resOFF_Files}`)

    // Depletion Row
    let toggleRow = true;
    let logScale = false;
    let dataLength=1;
    let timescanData = {};

    function sliceData(modifyData) {
 
        const reduceData = cloneDeep(modifyData)

        Object.keys(reduceData).forEach(data=>{
            Object.keys(reduceData[data]).forEach(innerData=>{
                const newData = reduceData[data][innerData]
                newData.x = newData.x.slice(timestartIndexScan, dataLength)
                newData.y = newData.y.slice(timestartIndexScan, dataLength)
                newData["error_y"]["array"] = newData["error_y"]["array"].slice(timestartIndexScan, dataLength)
                reduceData[data][innerData] = newData
            })

        })

        return cloneDeep(reduceData)
    }

    async function plotData({e=null, filetype="scan", tkplot="run"}={}){

        if (fileChecked.length === 0 && filetype === "scan") {return window.createToast("No files selected", "danger")}
        if (filetype === "general") {
            if (resOFF_Files === "" || resON_Files === "") {return window.createToast("No files selected", "danger")}
        }


        const depletionArgs = [JSON.stringify({
            currentLocation, resON_Files, resOFF_Files, 
            power, nshots, massIndex, timestartIndex, saveOutputDepletion
        })]
        
        let pyfileInfo = {
            scan: {pyfile:"timescan" , args:[[JSON.stringify({scanfiles, tkplot})]]},

            general: {pyfile:"depletionscan" , args: depletionArgs},
        }

        let {pyfile, args} = pyfileInfo[filetype]

        if (filetype == "scan") {graphPlotted = false}
        if (filetype == "general") {
            return computePy_func({e, pyfile, args, general:true, openShell})
        }

        try {
            const dataFromPython = await computePy_func({e, pyfile, args})

            if (filetype=="scan") {
                Object.keys(dataFromPython).forEach(data=>{
                    Object.keys(dataFromPython[data]).forEach(innerData=>{
                        dataLength = dataFromPython[data][innerData].x.length
                    })
                })
                timescanData = sliceData(dataFromPython)
                kineticData = sliceData(dataFromPython)

                fileChecked.forEach(file=>{
                    plot(`Timescan Plot: ${file}`, "Time (in ms)", "Counts", timescanData[file], `${file}_tplot`, logScale ? "log" : null)
                })
            } 
            window.createToast("Graph plotted", "success")
            graphPlotted = true
        } catch (error) {window.handleError(error)}
    }

    const linearlogCheck = () => {
        let layout = { yaxis: { title: "Counts", type: logScale ? "log" : null } }
        if(graphPlotted) {
            fileChecked.forEach(file => {
                let tplot = file + "_tplot";
                const id = document.getElementById(tplot)
                if(id?.data) {relayout(id, layout);}
            })
        }

    }

    let kineticMode = false;
    let kineticData = {}

    async function updateData(){
        kineticData = sliceData(timescanData)
        fileChecked.forEach(file=>{
            plot(`Timescan Plot: ${file}`, "Time (in ms)", "Counts", kineticData[file], `${file}_tplot`, logScale ? "log" : null)
        })
    }


    let saveOutputDepletion = true;

</script>

<ROSAAkinetics {fileChecked} {currentLocation} bind:kineticMode />

<Layout {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked on:chdir={dir_changed}>

    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Timescan Plot</button>

            <Textfield type="number" input$min=0 input$max={dataLength} bind:value={timestartIndexScan} label="Time Index" on:change={updateData}/>
            <button class="button is-link" on:click="{()=>{toggleRow = !toggleRow}}">Depletion Plot</button>
            <button class="button is-link" on:click="{()=>{kineticMode = !kineticMode}}">ROSAA Kinetics</button>
            
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"scan", tkplot:"plot"})}">Open in Matplotlib</button>
            <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomSwitch on:SMUISwitch:change={linearlogCheck} bind:selected={logScale} label="Log"/>
        </div>

        <div class="align animated fadeIn" class:hide={toggleRow} >
            <CustomSelect bind:picked={resON_Files} label="ResOn" options={fullfiles}/>
            <CustomSelect bind:picked={resOFF_Files} label="ResOFF" options={fullfiles}/>
            <Textfield bind:value={power} label="Power (ON, OFF) [mJ]" />
            <Textfield type="number" bind:value={nshots} label="FELIX Hz" />
            <Textfield type="number" bind:value={massIndex} label="Mass Index" />
            <Textfield type="number" bind:value={timestartIndex} label="Time Index" />
            <CustomSwitch bind:selected={saveOutputDepletion} label="save_output"/>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"general"})}">Submit</button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer" let:lookForGraph>
        <div class="graph__container" class:hide={!graphPlotted} >
            {#each fileChecked as scanfile}
                <div id="{scanfile}_tplot"  class="graph__div"  use:lookForGraph />
            {/each}
        </div>

    </svelte:fragment>
    
</Layout>

<style>

    .graph__container {
        display: flex;
    
        gap: 1em;
        flex-direction: column;
    }
</style>
