<script>
    import Textfield                    from '@smui/textfield'
    import Layout                       from "$components/Layout.svelte"
    import CustomSwitch                 from "$components/CustomSwitch.svelte"
    import CustomSelect                 from "$components/CustomSelect.svelte"
    import CustomIconSwitch             from "$components/CustomIconSwitch.svelte"
    import GetLabviewSettings           from "$components/GetLabviewSettings.svelte"
    import {relayout}                   from 'plotly.js/dist/plotly-basic';
    import {isEmpty}                    from "lodash-es"
    import {plot, plotlyEventsInfo}     from "$src/js/functions"
    import {readMassFile}               from "./masspec/mass"
    import computePy_func               from "$src/Pages/general/computePy"

    import {onDestroy}                  from "svelte";

    /////////////////////////////////////////////////////////////////////////

    // Initialisation
    const filetype = "mass"
    const id = "Masspec"
    let fileChecked = [];
    let currentLocation = ""
    $: massfiles = fs.existsSync(currentLocation) ? fileChecked.map(file=>pathResolve(currentLocation, file)) : []
    $: if(massfiles.length > 0) plotData()
    
    let openShell = false
    let graphPlotted = false
    let toggleRow1 = true
    let logScale = true;
    let selected_file = ""

    let peak_width = 2
    let peak_height = 40
    let peak_prominance = 3
    let keepAnnotaions = true
    
    async function plotData({e=null, filetype="mass"}={}){
        
        if (!fs.existsSync(currentLocation)) {return window.createToast("Location not defined", "danger")}

        if (fileChecked.length<1) {return window.createToast("No files selected", "danger")}
        if (filetype === "find_peaks") {if (selected_file === "") return window.createToast("No files selected", "danger")}


        const pyfileInfo = {
            mass: {pyfile:"mass" , args:[JSON.stringify({massfiles, tkplot:"run"})]},
            general: {pyfile:"mass" , args:[JSON.stringify({massfiles, tkplot:"plot"})]},
            find_peaks: {
                pyfile:"find_peaks_masspec",
                args:[JSON.stringify({
                    filename: pathResolve(currentLocation, selected_file),
                    peak_prominance, peak_width, peak_height
                })]
            },

        }
        const {pyfile, args} = pyfileInfo[filetype]
        
        if (filetype == "general") {await computePy_func({e, pyfile, args, general:true, openShell})}

        if (filetype=="mass" && massfiles) {

            const [dataFromPython] = await readMassFile(massfiles)
            if(isEmpty(dataFromPython)) return
            if(!keepAnnotaions) {$plotlyEventsInfo["mplot"].annotations=[]}
            
            plot("Mass spectrum", "Mass [u]", "Counts", dataFromPython, "mplot", logScale ? "log" : "linear", true)
            if(keepAnnotaions) {relayout("mplot" ,{annotations: $plotlyEventsInfo["mplot"].annotations})}
            
            graphPlotted = true
            
            return
        }
        
        if (filetype =="find_peaks") {
            const dataFromPython = await computePy_func({e, pyfile, args})
            
            relayout("mplot", { yaxis: { title: "Counts", type: "" } })
            relayout("mplot", { annotations: [] })
            relayout("mplot", { annotations: dataFromPython["annotations"] })
            relayout("mplot", { yaxis: { title: "Counts", type: "log" } })
        }
    }
    const linearlogCheck = () => {
        const layout = { yaxis: { title: "Counts", type: logScale ? "log" : null } }
        if(graphPlotted) relayout("mplot", layout)
    };

    let fullfileslist = [];
    onDestroy(()=>{
        if($plotlyEventsInfo.mplot) {$plotlyEventsInfo.mplot.eventCreated = false; $plotlyEventsInfo.mplot.annotations = []}
    })
</script>

<Layout {filetype} bind:fullfileslist {id} bind:currentLocation bind:fileChecked {graphPlotted} >

    <svelte:fragment slot="buttonContainer">
        <div class="align " style="align-items: center;">
            <button class="button is-link" on:click="{(e)=>plotData({e:e})}">Masspec Plot</button>
            <button class="button is-link" on:click="{()=>{toggleRow1 = !toggleRow1}}">Find Peaks</button>
            <GetLabviewSettings {currentLocation} {fullfileslist} {fileChecked} />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"general"})}">Open in Matplotlib</button>
            <CustomIconSwitch style="padding:0;" bind:toggler={openShell} icons={["settings_ethernet", "code"]}/>
            <CustomSwitch style="margin: 0 1em;" on:SMUISwitch:change={linearlogCheck} bind:selected={logScale} label="Log"/>
        </div>

        <div class="align animated fadeIn" class:hide={toggleRow1} >
            <CustomSelect bind:picked={selected_file} label="Filename" options={fileChecked}/>

            <Textfield type="number" on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_prominance} label="Prominance" />

            <Textfield type="number" on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_width} label="Width" />
            <Textfield type="number" on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_height} label="Height" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
            <button class="button is-danger" on:click="{()=> {if(graphPlotted) {relayout("mplot", { annotations: [] })} }}">Clear</button>
        </div>

    </svelte:fragment>

    <svelte:fragment slot="plotContainer"><div id="mplot" class="graph__div"></div></svelte:fragment>

    <svelte:fragment slot="plotContainer_functions" >
        <div class="align" style="justify-content: flex-end;">

            <CustomSwitch style="margin: 0 1em;" bind:selected={keepAnnotaions} label="Keep Annotaions"/>
            <button class="button is-danger" on:click="{()=> { $plotlyEventsInfo["mplot"].annotations = []; relayout("mplot" ,{annotations: []})}}">Clear</button>
        </div>

    </svelte:fragment>

</Layout>
