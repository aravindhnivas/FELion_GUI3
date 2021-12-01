<script>
    // import {mainPreModal} from "../svelteWritable";
    import Layout from "$components/Layout.svelte"
    import CustomIconSwitch from "$components/CustomIconSwitch.svelte"
    import CustomSelect from "$components/CustomSelect.svelte"
    import CustomSwitch from "$components/CustomSwitch.svelte"
    
    // import ReportLayout from "$components/ReportLayout.svelte"
    import Textfield from '@smui/textfield'
    import {plot} from "../js/functions.js"
    // import {Icon} from '@smui/icon-button'
    import GetLabviewSettings from "$components/GetLabviewSettings.svelte"

    /////////////////////////////////////////////////////////////////////////

    // Initialisation
    const filetype = "mass", id = "Masspec"
    let fileChecked = [];


    let currentLocation = db.get(`${filetype}_location`) || ""
    $: massfiles = fs.existsSync(currentLocation) ? fileChecked.map(file=>pathResolve(currentLocation, file)) : []
    
    let openShell = false, graphPlotted = false

    // Find peaks
    let toggleRow1 = true
    let selected_file = "", peak_prominance = 3, peak_width = 2, peak_height = 40;
    const style = "width:7em; height:3.5em; margin-right:0.5em"
    let logScale = true;
    let keepAnnotaions = true;
    // Functions
    function plotData({e=null, filetype="mass"}={}){

        if (!fs.existsSync(currentLocation)) {return window.createToast("Location not defined", "danger")}
        if (fileChecked.length<1) {return window.createToast("No files selected", "danger")}
        if (filetype === "find_peaks") {if (selected_file === "") return window.createToast("No files selected", "danger")}

        // console.log("Running")

        let pyfileInfo = {
            mass: {pyfile:"mass.py" , args:[JSON.stringify({massfiles, tkplot:"run"})]},
            general: {pyfile:"mass.py" , args:[JSON.stringify({massfiles, tkplot:"plot"})]},
            find_peaks: {
                pyfile:"find_peaks_masspec.py",
                args:[JSON.stringify({
                    filename: pathResolve(currentLocation, selected_file),
                    peak_prominance, peak_width, peak_height
                })]
            },

        }
        
        let {pyfile, args} = pyfileInfo[filetype]
        if (filetype == "general") {

            return computePy_func({e, pyfile, args, general:true, openShell}).catch(error=>{window.handleError(error)})
            
        }

        if (filetype == "mass") {graphPlotted = false}

        return computePy_func({e, pyfile, args})
                .then((dataFromPython)=>{

                    if (filetype=="mass") {
                        if(!keepAnnotaions) {annotations=[]}
                        plot("Mass spectrum", "Mass [u]", "Counts", dataFromPython, "mplot", logScale ? "log" : "linear")
                        if(keepAnnotaions) {window.Plotly.relayout("mplot" ,{annotations})}
                        plotlyEventCreatedMass ? console.log("Plotly event ready for mass spectrum") : plotlyClick()
                    } else if (filetype =="find_peaks") {

                        window.Plotly.relayout("mplot", { yaxis: { title: "Counts", type: "" } })
                        window.Plotly.relayout("mplot", { annotations: [] })
                    
                        window.Plotly.relayout("mplot", { annotations: dataFromPython["annotations"] })
                        
                        window.Plotly.relayout("mplot", { yaxis: { title: "Counts", type: "log" } })

                    }

                    window.createToast("Graph plotted", "success")
                    graphPlotted = true

                }).catch(error=>{window.handleError(error)})
        
    }

    // Linearlog check

    const linearlogCheck = () => {
        let layout = { yaxis: { title: "Counts", type: logScale ? "log" : null } }
        if(graphPlotted) window.Plotly.relayout("mplot", layout)
    };
    let fullfileslist = [];
    let plotlyEventCreatedMass = false
    let annotations = []

    function plotlyClick() {

        const mplot = document.getElementById("mplot")
        mplot.on('plotly_click', data => {
            if(data.event.ctrlKey) {
                const {points} = data
                const currentDataPoint = points[0]
                const {x: mass , y: counts } = currentDataPoint
                if(data.event.shiftKey) {
                    const annotate = _.find(annotations, (m) => {

                        const massValue = m.text.split(", ")[0].split("(")[1]
                        return massValue >= mass-0.2 && massValue <= mass+0.2
                    } )
                    annotations = _.differenceBy(annotations, [annotate], 'x')
                    console.log(annotations, annotate)
                } else {
                    const {color} = currentDataPoint.fullData.line
                    const annotate = { 
                        text: `(${mass}, ${counts})`, 
                        x: mass, y: logScale ? Math.log10(counts): counts, xref: 'x', yref: 'y', 
                        font: {color}, showarrow: true, arrowhead: 2, arrowcolor: color
                    }
                    annotations = [...annotations, annotate]

                }
                window.Plotly.relayout("mplot" ,{annotations})
                plotlyEventCreatedMass = true
            }
        })
    }
</script>

<Layout  {filetype} bind:fullfileslist {id} bind:currentLocation bind:fileChecked {graphPlotted} >

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
            <CustomSelect style="width:12em; height:3.5em; margin-right:0.5em" bind:picked={selected_file} label="Filename" options={["", ...fileChecked]}/>

            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_prominance} label="Prominance" />

            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_width} label="Width" />
            <Textfield type="number" {style} on:change="{(e)=>plotData({e:e, filetype:"find_peaks"})}" bind:value={peak_height} label="Height" />
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"find_peaks"})}">Get Peaks</button>
            <button class="button is-danger" on:click="{()=> {if(graphPlotted) {window.Plotly.relayout("mplot", { annotations: [] })} }}">Clear</button>
        </div>

    </svelte:fragment>

    <svelte:fragment slot="plotContainer"><div id="mplot" class="graph__div"></div></svelte:fragment>

    <svelte:fragment slot="plotContainer_functions" >
        <div class="align" style="justify-content: flex-end;">
            <CustomSwitch style="margin: 0 1em;" bind:selected={keepAnnotaions} label="Keep Annotaions"/>
            <button class="button is-danger" on:click="{()=> { annotations = []; window.Plotly.relayout("mplot" ,{annotations})}}">Clear</button>

        </div>

    </svelte:fragment>

</Layout>