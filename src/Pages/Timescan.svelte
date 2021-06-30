
<script>
    import {mainPreModal} from "../svelteWritable";
    import Layout from "../components/Layout.svelte"
    import CustomIconSwitch from "../components/CustomIconSwitch.svelte"
    import CustomSelect from "../components/CustomSelect.svelte"
    import CustomSwitch from "../components/CustomSwitch.svelte"

    import ReportLayout from "../components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import {plot} from "../js/functions.js"
    /////////////////////////////////////////////////////////////////////////

    // Initialisation

    const filetype = "scan", id = "Timescan"
    let fileChecked = [];
    let currentLocation = db.get(`${filetype}_location`) || ""

    $: scanfiles = fileChecked.map(file=>path.resolve(currentLocation, file))
    
    let openShell = false, graphPlotted = false
    
    let massIndex = 0, timestartIndex = 1, nshots = 10, power = "21, 21", resON_Files = "", resOFF_Files = ""
    let fullfiles = []

    function dir_changed() {
        // console.log("Directory changed/refreshed", event)
        if (fs.existsSync(currentLocation)) {
            fullfiles = ["", ...fs.readdirSync(currentLocation).filter(file=>file.endsWith(".scan"))]
        }
    }

    $: console.log(`ResOn: ${resON_Files}\nResOff: ${resOFF_Files}`)

    // Depletion Row
    let toggleRow = true
    let style = "width:7em; height:3.5em; margin-right:0.5em"

    // Linear log
    let logScale = false;

    function plotData({e=null, filetype="scan", tkplot="run"}={}){

        if (fileChecked.length === 0 && filetype === "scan") {return window.createToast("No files selected", "danger")}

        if (filetype === "general") {
            if (resOFF_Files === "" || resON_Files === "") {return window.createToast("No files selected", "danger")}
        }
        
        let pyfileInfo = {
            scan: {pyfile:"timescan.py" , args:[...scanfiles, tkplot]},
        
            general: {pyfile:"depletionscan.py" , args:[currentLocation,
                resON_Files, resOFF_Files, ...power.split(",").map(pow=>parseFloat(pow)), nshots, massIndex, timestartIndex]},
        }
        let {pyfile, args} = pyfileInfo[filetype]

        // if (tkplot == "plot") {filetype = "general"}
        if (filetype == "scan") {graphPlotted = false}
        if (filetype == "general") {

            return computePy_func({e, pyfile, args, general:true, openShell}).catch(err=>{$mainPreModal.modalContent = err;  $mainPreModal.open = true})
        }



        return computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{
                    if (filetype=="scan") {
                        fileChecked.forEach(file=>{
                                plot(`Timescan Plot: ${file}`, "Time (in ms)", "Counts", dataFromPython[file], `${file}_tplot`)
                            })
                    } 
                    window.createToast("Graph plotted", "success")

                    graphPlotted = true

                }).catch(err=>{$mainPreModal.modalContent = err;  $mainPreModal.open = true})

    }

    // Linearlog check
    const linearlogCheck = () => {
        let layout = { yaxis: { title: "Counts", type: logScale ? "log" : null } }
        if(graphPlotted) {

            fileChecked.forEach(file => {
                let tplot = file + "_tplot";
                Plotly.relayout(tplot, layout);
            })
        }
    }

    $: includePlotsInReport = fileChecked.map(file=>file={id:`${file}_tplot`, include:false, label:file})

</script>

<Layout {filetype} {graphPlotted} {id} bind:currentLocation bind:fileChecked on:chdir={dir_changed}>

    <svelte:fragment slot="buttonContainer">

        <div class="align " style="align-items: center;">
            <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Timescan Plot</button>
            <button class="button is-link" on:click="{()=>{toggleRow = !toggleRow}}">Depletion Plot</button>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"scan", tkplot:"plot"})}">Open in Matplotlib</button>
            <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomSwitch on:change={linearlogCheck} bind:selected={logScale} label="Log"/>
        </div>

        <div class="align animated fadeIn " class:hide={toggleRow} >
            <CustomSelect bind:picked={resON_Files} label="ResOn" options={fullfiles}/>
            <CustomSelect bind:picked={resOFF_Files} label="ResOFF" options={fullfiles}/>
            <Textfield bind:value={power} label="Power (ON, OFF) [mJ]" />
            <Textfield type="number" {style} bind:value={nshots} label="FELIX Hz" />
            <Textfield type="number" {style} bind:value={massIndex} label="Mass Index" />
            <Textfield type="number" {style} bind:value={timestartIndex} label="Time Index" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"general"})}">Submit</button>
        </div>

    </svelte:fragment>

    <div style="margin-right: 1em;" slot="plotContainer">
        <div id="tplotContainer">

            {#each fileChecked as scanfile}
            
                <div id="{scanfile}_tplot" style="padding-bottom:1em" />
            {/each}
        
        </div>

        
        
        {#if graphPlotted}

            <div class="animated fadeIn" style="flex-direction:column ">
                <ReportLayout bind:currentLocation={currentLocation} id={`${filetype}_report`} {includePlotsInReport} />

            </div>
        {/if}
        
        
    </div>
    
</Layout>