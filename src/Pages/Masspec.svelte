<script>
    import {mainPreModal} from "../svelteWritable";
    import Layout from "../components/Layout.svelte"
    import CustomIconSwitch from "../components/CustomIconSwitch.svelte"
    import CustomSelect from "../components/CustomSelect.svelte"
    import CustomSwitch from "../components/CustomSwitch.svelte"
    
    // import ReportLayout from "../components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import {plot} from "../js/functions.js"
    import {Icon} from '@smui/icon-button'
    import GetLabviewSettings from "../components/GetLabviewSettings.svelte"

    /////////////////////////////////////////////////////////////////////////

    // Initialisation
    const filetype = "mass", id = "Masspec"
    let fileChecked = [];


    let currentLocation = db.get(`${filetype}_location`) || ""
    $: massfiles = existsSync(currentLocation) ? fileChecked.map(file=>pathResolve(currentLocation, file)) : []
    
    let openShell = false, graphPlotted = false

    // Find peaks
    let toggleRow1 = true

    let selected_file = "", peak_prominance = 3, peak_width = 2, peak_height = 40;
    const style = "width:7em; height:3.5em; margin-right:0.5em"

    // NIST 
    let toggleRow2 = true, nist_molecule = localStorage["nist_molecule"] || "", nist_formula = localStorage["nist_formula"] || ""
    const style2 = "width:12em; height:3em; margin-right:0.5em"

    $: nist_molecule_name = `Name=${nist_molecule}`
    $: nist_molecule_formula = `Formula=${nist_formula}`
    let nist_url = localStorage["nist_url"] || "https://webbook.nist.gov/cgi/cbook.cgi?Name=&Units=SI&Mask=200#Mass-Spec"

    const set_nist_url = (format="") => {
        let fmt;
        format == "by_name" ? fmt = nist_molecule_name : fmt = nist_molecule_formula
        nist_url = `https://webbook.nist.gov/cgi/cbook.cgi?${fmt}&Units=SI&Mask=200#Mass-Spec`
        localStorage["nist_url"] = nist_url
        localStorage["nist_formula"] =  nist_formula
        localStorage["nist_molecule"] = nist_molecule
    }

    // Linear log
    let logScale = true;

    // Functions
    function plotData({e=null, filetype="mass"}={}){

        if (!existsSync(currentLocation)) {return window.createToast("Location not defined", "danger")}
        if (fileChecked.length<1) {return window.createToast("No files selected", "danger")}
        if (filetype === "find_peaks") {if (selected_file === "") return window.createToast("No files selected", "danger")}

        // console.log("Running")

        let pyfileInfo = {
            mass: {pyfile:"mass.py" , args:[...massfiles, "run"]},
            general: {pyfile:"mass.py" , args:[...massfiles, "plot"]},
            find_peaks: {pyfile:"find_peaks_masspec.py" , args:[pathResolve(currentLocation, selected_file), peak_prominance, peak_width, peak_height]},

        }
        
        let {pyfile, args} = pyfileInfo[filetype]
        if (filetype == "general") {

            return computePy_func({e, pyfile, args, general:true, openShell}).catch(error=>{mainPreModal.error(error.stack || error)})
            
        }

        if (filetype == "mass") {graphPlotted = false}

        return computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{

                    if (filetype=="mass") {
                    
                        plot("Mass spectrum", "Mass [u]", "Counts", dataFromPython, "mplot", "log")
                    
                    } else if (filetype =="find_peaks") {

                        Plotly.relayout("mplot", { yaxis: { title: "Counts", type: "" } })
                        Plotly.relayout("mplot", { annotations: [] })
                    
                        Plotly.relayout("mplot", { annotations: dataFromPython["annotations"] })
                        
                        Plotly.relayout("mplot", { yaxis: { title: "Counts", type: "log" } })

                    }

                    window.createToast("Graph plotted", "success")
                    graphPlotted = true

                }).catch(error=>{mainPreModal.error(error.stack || error)})
        
    }

    // Linearlog check

    const linearlogCheck = () => {
        let layout = { yaxis: { title: "Counts", type: logScale ? "log" : null } }
        if(graphPlotted) Plotly.relayout("mplot", layout)
    };
    
    let includePlotsInReport = [{id:"mplot", include:true, label:"Mass Spectrum"}]

    let fullfileslist = [];
</script>


<style>

</style>

<Layout  {filetype} bind:fullfileslist {id} bind:currentLocation bind:fileChecked {graphPlotted}>
    <svelte:fragment slot="buttonContainer">

        <div class="content align " style="align-items: center;">
            <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Masspec Plot</button>
            <button class="button is-link" on:click="{()=>{toggleRow1 = !toggleRow1}}">Find Peaks</button>
            <button class="button is-link" on:click="{()=>{toggleRow2 = !toggleRow2}}">NIST Webbook</button>
            <GetLabviewSettings {currentLocation} {fullfileslist}/>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"general"})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomSwitch style="margin: 0 1em;" on:change={linearlogCheck} bind:selected={logScale} label="Log"/>
        </div>

        <div class="align animated fadeIn" class:hide={toggleRow1} >
            <CustomSelect style="width:12em; height:3.5em; margin-right:0.5em" bind:picked={selected_file} label="Filename" options={["", ...fileChecked]}/>
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_prominance} label="Prominance" />
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_width} label="Width" />
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_height} label="Height" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
            <button class="button is-danger" on:click="{()=> {if(graphPlotted) {Plotly.relayout("mplot", { annotations: [] })} }}">Clear</button>

        </div>
        <div class="align animated fadeIn " class:hide={toggleRow2}>
            <Textfield {style2} on:change="{()=>set_nist_url("by_name")}" bind:value={nist_molecule} label="Molecule Name" />

                <Textfield {style2} on:change={set_nist_url} bind:value={nist_formula} label="Molecule Formula" />
        </div>

    </svelte:fragment>

    <div style="margin-right: 1em;" slot="plotContainer">

        <div id="mplot" class="graph__div"></div>
       
        <div class="align animated fadeIn" class:hide={toggleRow2}>
            <Icon on:click="{()=>window.nist_webview.goToIndex(0)}" class="material-icons hvr-glow">home</Icon>
            <Icon on:click="{()=>window.nist_webview.reload()}" class="material-icons hvr-glow">refresh</Icon>
            <Icon on:click="{()=>{if(window.nist_webview.canGoBack()) {window.nist_webview.goBack()}}}" class="material-icons hvr-glow">arrow_left</Icon>

            <Icon on:click="{()=>{if(window.nist_webview.canGoForward()) {window.nist_webview.goForward()}}}" class="material-icons hvr-glow">arrow_right</Icon>
            <webview src={nist_url} id="nist_webview" style="height: 50vh; padding-bottom:3em; width: 100%; "></webview>
        </div>

    </div>

</Layout>