
<script>
    // import {mainPreModal} from "../svelteWritable";
    import Layout from "$components/Layout.svelte"
    import CustomIconSwitch from "$components/CustomIconSwitch.svelte"
    import CustomSelect from "$components/CustomSelect.svelte"
    import CustomSwitch from "$components/CustomSwitch.svelte"

    import ROSAAkinetics from "../Pages/timescan/components/ROSAAkinetics.svelte"
    import Textfield from '@smui/textfield'
    import {plot} from "../js/functions.js"
    /////////////////////////////////////////////////////////////////////////

    // Initialisation

    const filetype = "scan", id = "Timescan"

    let fileChecked = [];
    let currentLocation = db.get(`${filetype}_location`) || ""
    $: scanfiles = fileChecked.map(file=>pathResolve(currentLocation, file))
    let openShell = false, graphPlotted = false
    let massIndex = 0, timestartIndex = 1, nshots = 10, power = "21, 21", resON_Files = "", resOFF_Files = "";
    let timestartIndexScan = 0;
    let fullfiles = []
    function dir_changed() {
        if (fs.existsSync(currentLocation)) {
            fullfiles = ["", ...fs.readdirSync(currentLocation).filter(file=>file.endsWith(".scan"))]
        }
    }
    $: console.log(`ResOn: ${resON_Files}\nResOff: ${resOFF_Files}`)

    // Depletion Row
    let toggleRow = true;
    let style = "width:7em; height:3.5em; margin-right:0.5em"
    let logScale = false;

    let timescanData = {};
    let dataLength=1;
    function sliceData(modifyData) {
        const reduceData = _.cloneDeep(modifyData)
        Object.keys(reduceData).forEach(data=>{
            Object.keys(reduceData[data]).forEach(innerData=>{
                const newData = reduceData[data][innerData]
                newData.x = newData.x.slice(timestartIndexScan, dataLength)
                newData.y = newData.y.slice(timestartIndexScan, dataLength)
                newData["error_y"]["array"] = newData["error_y"]["array"].slice(timestartIndexScan, dataLength)
                reduceData[data][innerData] = newData
            })

        })

        return _.cloneDeep(reduceData)
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
            scan: {pyfile:"timescan.py" , args:[...scanfiles, tkplot]},

            general: {pyfile:"depletionscan.py" , args: depletionArgs},
        }

        let {pyfile, args} = pyfileInfo[filetype]

        if (filetype == "scan") {graphPlotted = false}
        if (filetype == "general") {

            return computePy_func({e, pyfile, args, general:true, openShell}).catch(error=>{window.handleError(error)})
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
                if(id?.data) {Plotly.relayout(id, layout);}
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


<ROSAAkinetics {fileChecked} {currentLocation} bind:kineticMode {kineticData}/>



<Layout {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked on:chdir={dir_changed}>

    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Timescan Plot</button>

            <Textfield type="number" input$min=0 input$max={dataLength} {style} bind:value={timestartIndexScan} label="Time Index" on:change={updateData}/>
            <button class="button is-link" on:click="{()=>{toggleRow = !toggleRow}}">Depletion Plot</button>
            <button class="button is-link" on:click="{()=>{kineticMode = !kineticMode}}">ROSAA Kinetics</button>
            
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"scan", tkplot:"plot"})}">Open in Matplotlib</button>
            <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomSwitch on:change={linearlogCheck} bind:selected={logScale} label="Log"/>
        </div>

        <div class="align animated fadeIn" class:hide={toggleRow} >
            <CustomSelect style="min-width: 7em;" bind:picked={resON_Files} label="ResOn" options={fullfiles}/>
            <CustomSelect style="min-width: 7em;" bind:picked={resOFF_Files} label="ResOFF" options={fullfiles}/>
            <Textfield bind:value={power} label="Power (ON, OFF) [mJ]" />
            <Textfield type="number" {style} bind:value={nshots} label="FELIX Hz" />
            <Textfield type="number" {style} bind:value={massIndex} label="Mass Index" />
            <CustomSwitch bind:selected={saveOutputDepletion} label="save_output"/>
            <Textfield type="number" {style} bind:value={timestartIndex} label="Time Index" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"general"})}">Submit</button>
        </div>
    </svelte:fragment>

    <svelte:fragment slot="plotContainer" let:lookForGraph>
        {#each fileChecked as scanfile}
            <div id="{scanfile}_tplot" class="graph__div" style="padding-bottom:1em" use:lookForGraph />
        {/each}

    </svelte:fragment>
    
</Layout>

