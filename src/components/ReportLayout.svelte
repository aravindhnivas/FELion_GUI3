<script context="module">
    export async function asyncForEach(array, callback) {
        for (let index = 0; index < array.length; index++) {
            await callback(array[index], index, array);
        }
    }
</script>

<script>

    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'
    import CustomCheckbox from './CustomCheckbox.svelte'
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index'
    import Ripple from '@smui/ripple'

    import {createToast} from "./Layout.svelte"
    
    import Select, {Option} from '@smui/select'
    import {onMount} from "svelte";
    import Hamburger1 from "./icon_animations/Hamburger1.svelte";
    import PreModal from "./PreModal.svelte";
    const {BrowserWindow} = remote
    //////////////////////////////////////////////////////////////////////////////////////////////////

    export let currentLocation = "", id="report", includePlotsInReport=[], includeTablesInReports=[]
    $: reportFile = path.resolve(currentLocation, `reports/${reportMolecule}_report.html`)
    let reportTitle = "", reportComments = "", reportMethod = "info", reportMolecule = ""
    const stylesheet = path.resolve(__dirname, 'assets/reports/template.css')
    const reportHTML = document.createElement( 'html' )

    let preModal = {};

    function init_report(){


        const reportExist = fs.existsSync(reportFile)
        console.log("Report status:\n", reportExist)

        const reportHTMLTemplate = `<!DOCTYPE html>
                                <html lang="en">
                                    <head>
                                        <meta charset='utf8'>
                                        <meta name="viewport" content="width=device-width, initial-scale=1">
                                        <meta http-equiv="X-UA-Compatible" content="ie=edge">
                                        <title>${reportMolecule} Reports</title>
                                        <link rel="stylesheet" type='text/css' href="report_stylesheet.css">
                                    </head>

                                    <body>
                                        <section class="section" id="mainSection"></section>
                                    </body>
                                </html>`

        reportHTML.innerHTML = reportExist ? fs.readFileSync(reportFile) : reportHTMLTemplate
        console.log("ReportHTML: ", reportHTML)
        reportMainContainer = reportHTML.querySelector("#mainSection")
    }
    
    function getImage(imgID) {
        return new Promise(resolve => {
            Plotly.toImage(imgID, {format: 'png', width: 1000, height: 500}).then(dataURL =>{resolve(dataURL)})
        })
        
    }
    
    const exprtToHtml = async (content) => {

        fs.writeFile(reportFile, content, function(err) {

            if(err) {
                createToast("Report couldn't be added.", "danger")
                return console.log(err);
            }
            
            let local_cssFile = path.resolve(currentLocation, 'reports/report_stylesheet.css')
        
            if (!fs.existsSync(local_cssFile)){
                fs.copyFile(stylesheet, local_cssFile, (err) => {
                    if (err) throw err;
                    console.log('template.css file copied');
                });
            }
            createToast("Report added", "success")

            console.log("Exported to HTML")
        })

        reportTitle = "", reportComments = ""
        
    }

    const addReport = async() => {

        let reportDir = path.resolve(currentLocation, "reports")
        if (!fs.existsSync(reportDir)) {fs.mkdirSync(reportDir); console.log("reports directory created")}
        
        const reportCount = reportMainContainer.getElementsByClassName("reportCount").length
        if (reportTitle.length == 0) reportTitle = `Title-${reportCount}`
        if (reportComments.length == 0) reportComments = "-"

        
        let tableDiv = document.createElement("div")
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
                    
                } catch (error) {
                    createToast(`${tb.label} is not visible`, "danger")
                }
            }
        
        })

        console.log("tableDiv created", tableDiv)
        

        let plotDiv = document.createElement("div")
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

        let reportMainHeading = document.createElement("h1")
        reportMainHeading.setAttribute("class", `notification is-${reportMethod} reportHeading`)
        reportMainHeading.textContent = reportTitle

        let reportComment = document.createElement("div")
        reportComment.setAttribute("class", "reportComments")

        let reportDiv = document.createElement("div")
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
                        fs.writeFile(reportFile.replace(".html", ".pdf"), data, (error) => {
                            if (error) {preModal.modalContent = error; preModal.open = true; return}
                            createToast('Write PDF successfully.', "success")
                        })
                    }).catch(error => { preModal.modalContent = error; preModal.open = true })

                } else {
                    reportWindow.webContents.printToPDF({printBackground: true, landscape:landscape, pageSize:pageSize}, (error, data) => {
                        if(error) { preModal.modalContent = error; preModal.open = true; return}
                        fs.writeFile(reportFile.replace(".html", ".pdf"), data, (error) => {
                            if (error) {preModal.modalContent = error; preModal.open = true; return}
                            createToast('Write PDF successfully.', "success")
                        })
                    })
                }
            }
        })
        
    }

    const notificationMethod = [{name:"info", color:"white"}, {name:"success", color:"#00ff00"}, {name:"warning", color:"yellow"}, {name:"danger", color:"red"}]
    let reportMainContainer;
    onMount(()=>{
        init_report()
    })
    let toggle = false;
</script>

<style>

    /* .notification { margin-top: 1em; border: 1px solid; } */
    .button {margin-right: 1em;}
    .report {display: flex; align-items: inherit; flex-direction: column;}
    .addToReport > hr {margin: auto; width: 50%;}
    .addToReport > h1 {margin: 5px 0; justify-content: center; display: flex;}

    .addToReport > div {margin: 1em 0; justify-content: center; display: flex; flex-wrap: wrap;}
    .align {display: flex; align-items: center;}
    .heading {
        border: 1px solid;
        margin: 1em 0;
        background-color: #634e96;
        border-radius: 5px;
    }

    .title {margin: 0; flex-grow: 2;}

</style>
<PreModal bind:preModal/>
<div class="content align heading">

    <div class="title notification is-link">Add to report</div>
    <Hamburger1 bind:active={toggle}/>
    
</div>

{#if toggle}

    <div style="margin-bottom:1em;">
        <Textfield style="height:3em; width:20em;" variant="outlined" bind:value={reportMolecule} label="Molecule Name" />
        <button class="button is-pulled-right is-warning" on:click="{()=>{ reportMainContainer.innerHTML = ""; exprtToHtml(""); createToast("Report resetted", "warning")}}">Reset Report</button>
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
                <hr>
                    <h1 class="subtitle">Include tables</h1>
                <hr>
                <div class="">
                    {#each includeTablesInReports as {id, include, label}(id)}
                        <CustomCheckbox bind:selected={include} {label}/>
                    {/each}
                </div>
            </div>
        {/if}
        
        
        <div class="addToReport ">
            <hr>
                <h1 class="subtitle">Include plots</h1>
            <hr>
            <div class="">
                {#each includePlotsInReport as {id, include, label}(id)}
                    <CustomCheckbox bind:selected={include} {label}/>
                {/each}
            </div>
        </div>

        <Textfield style="height:3em; margin-bottom:1em;" variant="outlined" bind:value={reportTitle} label="Title" />
        <Textfield textarea bind:value={reportComments} label="Comments"  
            input$aria-controls="{id}_comments" input$aria-describedby="{id}_comments"/>
        <HelperText id="{id}_comments">
            {"NOTE: You can write in markdown format (eg: # Title, ## Subtilte, **bold**, _italics_, > BlockQuotes, >> Nested BlockQuotes,  1., 2. for list, etc.,)"}
        </HelperText>

        <div class="align" style="margin-top:1em;">
        
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click={addReport}>Add to Report</button>
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click={showReport}>Show Report</button>
            <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click="{()=>showReport({export_pdf:true})}">EXPORT to PDF</button>
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

{/if}