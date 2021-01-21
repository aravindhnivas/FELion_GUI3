
<script>
    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'
    import CustomCheckbox from './CustomCheckbox.svelte'
    import Textfield from '@smui/textfield'
    import Select, {Option} from '@smui/select'

    import {onMount} from "svelte";
    import Hamburger1 from "./icon_animations/Hamburger1.svelte";
    import PreModal from "./PreModal.svelte";
    import Editor from "./Editor.svelte";

    const {BrowserWindow} = remote

    //////////////////////////////////////////////////////////////////////////////////////////////////

    export let currentLocation = "", id="report", includePlotsInReport=[], includeTablesInReports=[]
    let reportTitle = "", reportMethod = "info", reportMolecule = ""
    $: reportFile = path.resolve(currentLocation, `reports/${reportMolecule}_report.html`)
    // const reportExist = fs.existsSync(reportFile)
    const stylesheet1 = path.resolve(__dirname, `assets/reports/report.css`)
    const stylesheet2 = path.resolve(__dirname, `assets/reports/template.css`)
    const reportHTML = document.createElement( 'html' )

    let preModal = {};

    $: reportHTMLTemplate = `<!DOCTYPE html>
                                <html lang="en">
                                    <head>
                                        <meta charset='utf8'>
                                        <meta name="viewport" content="width=device-width, initial-scale=1">
                                        <meta http-equiv="X-UA-Compatible" content="ie=edge">
                                        <title>${reportMolecule} Reports</title>
                                        <link rel="stylesheet" type='text/css' href="${stylesheet1}">
                                        <link rel="stylesheet" type='text/css' href="${stylesheet2}">
                                    </head>

                                    <body>
                                        <section class="section" id="mainSection"></section>
                                    </body>
                                </html>`


    function init_report(){

        reportHTML.innerHTML = fs.existsSync(reportFile) ? fs.readFileSync(reportFile) : reportHTMLTemplate
        console.log("ReportHTML: ", reportHTML)
        reportMainContainer = reportHTML.querySelector("#mainSection")
        
        const reportDir = path.resolve(currentLocation, "reports")

        if (!fs.existsSync(reportDir)) {
            fs.mkdir(reportDir, { recursive: true }, (err) => {

                if (err) return window.createToast("No write access for making report", "danger");
                console.log("reports directory created")
            });
        }
    }
    
    let plotWidth = 750, plotHeight = 500;
    function getImage(imgID) {

        return new Promise(resolve => {

            Plotly.toImage(imgID, {format: 'png', width: plotWidth, height: plotHeight}).then(dataURL =>{resolve(dataURL)})
        
        })
    
    }


    const exprtToHtml = async (content) => {
        fs.writeFile(reportFile, content || reportHTMLTemplate, function(err) {

            if(err) {
                window.createToast("Report couldn't be added.", "danger")
                return console.log(err);
            }
            window.createToast("Report added", "success")

            console.log("Exported to HTML")
        })

        reportTitle = ""
        
    }

    const addTablesToReport = () => {

        const tableDiv = document.createElement("div")
        tableDiv.setAttribute("class", "content reportTable")
        
        includeTablesInReports.forEach(tb=>{

            if(tb.include) {

                try {

                    let tableContent = document.getElementById(tb.id).innerHTML
                
                    let tableElement = document.createElement("table")
                    
                    tableElement.setAttribute("class", "table is-bordered is-hoverable")
                    tableElement.innerHTML = tableContent

                    
                    let tableHeading = document.createElement("h1")
                    tableHeading.setAttribute("class", "title")
                    
                    tableHeading.textContent = tb.label
                    
                    tableDiv.appendChild(tableHeading)
                    tableDiv.appendChild(tableElement)
                    
                } catch (err) {
                    window.createToast(`${tb.label} is not visible`, "danger")
                }

            }
        
        })
        console.log("tableDiv created", tableDiv)

        return tableDiv
    }


    const addPlotImagesToReport = async () => {

        const plotDiv = document.createElement("div")
        plotDiv.setAttribute("class", "content reportPlots")

        await asyncForEach(includePlotsInReport, async (plot)=>{
            if (plot.include) {
                console.log("Request Image URL for ", plot.id)


                let imgURL = await getImage(plot.id)
                console.log(`Received Image URL for ${plot.id}\n`)
                let imgElement = document.createElement("img")

                imgElement.setAttribute("src", imgURL)
                plotDiv.appendChild(imgElement)
                console.log(`${plot.id} Included in HTML`)

            }
        
        })
        console.log("plotDiv created", plotDiv)
        
        return Promise.resolve(plotDiv)

    }

    let reportEditor;
    const addReport = async () => {

        if(!fs.existsSync(reportFile)) {init_report()}
        const tableDiv = addTablesToReport()
        const plotDiv = await addPlotImagesToReport()

        const reportMainHeading = document.createElement("h1")

        reportMainHeading.setAttribute("class", `notification is-${reportMethod} reportHeading`)

        reportMainHeading.textContent = reportTitle

        const reportComment = document.createElement("div")
        
        reportComment.setAttribute("class", "reportComments")
        
        reportComment.innerHTML = reportEditor.root.outerHTML

        const reportDiv = document.createElement("div")
        reportDiv.setAttribute("class", "content reportCount")

        reportDiv.appendChild(reportMainHeading)
        reportDiv.appendChild(reportComment)
        reportDiv.appendChild(plotDiv)
        reportDiv.appendChild(tableDiv)

        console.log("reportDiv div created", reportDiv)

        reportMainContainer.appendChild(reportDiv)
        console.log("reportMainContainer div created", reportMainContainer)

        console.log("Full report\n", reportHTML)
        exprtToHtml(reportHTML.innerHTML)
    }


    let exportMethod = "landscape", pageSize = "A4"

    const showReport = ({export_pdf=false}={}) => {

        let reportWindow = new BrowserWindow({ width: 1200, minWidth :600, height: 600, parent: remote.getCurrentWindow(), show:!export_pdf})
        reportWindow.on('closed', () => { reportWindow = null; console.log("Report window closed") })
        reportWindow.loadURL(reportFile)
        reportWindow.webContents.on('did-finish-load', ()=>{ 
            console.log("Report loaded")
            if(export_pdf) {

                let landscape;
                exportMethod == "landscape" ? landscape = true : landscape = false
                
                if (process.versions.electron >= "7") {
                    reportWindow.webContents.printToPDF({printBackground: true, landscape:landscape, pageSize:pageSize})
                    .then(data => {
                        fs.writeFile(reportFile.replace(".html", ".pdf"), data, (err) => {
                            if (err) {preModal.modalContent = err.stack; preModal.open = true; return}
                            window.createToast('Write PDF successfully.', "success")
                        })
                    }).catch(err => { preModal.modalContent = err.stack; preModal.open = true })

                } else {
                    reportWindow.webContents.printToPDF({printBackground: true, landscape:landscape, pageSize:pageSize}, (err, data) => {
                        if(err) { preModal.modalContent = err.stack; preModal.open = true; return}
                        fs.writeFile(reportFile.replace(".html", ".pdf"), data, (err) => {
                            if (err) {preModal.modalContent = err.stack; preModal.open = true; return}
                            window.createToast('Write PDF successfully.', "success")
                        })
                    })
                }
            }
        })
        
    }

    const notificationMethod = [{name:"info", color:"white"}, {name:"success", color:"#00ff00"}, {name:"warning", color:"yellow"}, {name:"danger", color:"red"}]
    let reportMainContainer;

    onMount(()=>{ init_report() })

    let toggle = false;
</script>

<style>

    .button {margin-right: 1em;}



    .report {display: flex; align-items: inherit; flex-direction: column;}
    .addToReport > div {justify-content: center; display: flex; flex-wrap: wrap;}

    .align {display: flex; align-items: center;}
    .heading {
    
        border: 1px solid;
        margin: 1em 0;
        background-color: #634e96;



        border-radius: 5px;
    }

    .title {margin: 0; flex-grow: 2;}
    .hide {display: none;}

</style>
<PreModal bind:preModal/>

<div class="content align heading">
    <div class="title notification is-link">Add to report</div>
    <Hamburger1 bind:active={toggle}/>

</div>

<div class:hide={!toggle} class="animated fadeIn">


    <div style="margin-bottom:1em;">
        <Textfield style="height:3em; width:20em;" variant="outlined" bind:value={reportMolecule} label="Molecule Name" />
        <button class="button is-pulled-right is-warning" on:click="{()=>{ reportMainContainer.innerHTML = ""; exprtToHtml(""); window.createToast("Report resetted", "warning")}}">Reset Report</button>
    </div>

    <div class="align report" {id} >
        <div class="">
            {#each notificationMethod as method}
                <FormField >
                    <Radio bind:group={reportMethod} value={method.name}  />
                    
                    <span slot="label" style="color:{method.color}">{method.name}</span>
                </FormField>
            {/each}
        </div>

        {#if includeTablesInReports.length>0}
            <div class="addToReport ">
                <div class="">
                    {#each includeTablesInReports as {id, include, label}(id)}
                        <CustomCheckbox bind:selected={include} {label}/>
                    {/each}
                </div>
            </div>
        {/if}
        
        
        <div class="addToReport ">

            <div class="">
                {#each includePlotsInReport as {id, include, label}(id)}
                    <CustomCheckbox bind:selected={include} {label}/>
                {/each}
        
        
            </div>
        </div>

        <Textfield style="height:3em; margin-bottom:1em;" variant="outlined" bind:value={reportTitle} label="Title" />
        <Editor bind:reportEditor {id}/>
        
        
        <div class="align" style="margin-top:1em;">
            <button class="button is-link" on:click={addReport}>Add to Report</button>
            <button class="button is-link" on:click={showReport}>Show Report</button>
        
        </div>

        <div class="align">
            <Textfield style="width:7em;" variant="outlined" bind:value={plotWidth} label="plotWidth" />
            <Textfield style="width:7em;" variant="outlined" bind:value={plotHeight} label="plotHeight" />
            
            
            <button class="button is-link" on:click="{()=>showReport({export_pdf:true})}">EXPORT to PDF</button>

            {#each ["landscape", "portrait"] as method}
            
                <FormField >
            
                    <Radio bind:group={exportMethod} value={method}  />

                    <span slot="label" style="color:{method}">{method}</span>
            
                </FormField>
            {/each}

            <Select bind:value={pageSize} label="pageSize" style="margin-left:1em;">
                {#each ["A3", "A4", "A5", "Legal", "Letter"] as file}
                    <Option value={file} selected={pageSize  === file}>{file}</Option>
                {/each}
            </Select>
        </div>
    
    </div>

</div>