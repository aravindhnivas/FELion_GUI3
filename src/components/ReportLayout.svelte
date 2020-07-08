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
    
    const {BrowserWindow} = remote
    import {modalContent, activated} from "./Modal.svelte"
    import Select, {Option} from '@smui/select'
    //////////////////////////////////////////////////////////////////////////////////////////////////

    export let currentLocation = "", id="report", includePlotsInReport=[], includeTablesInReports=[]
    
    $: reportFile = path.resolve(currentLocation, `reports/${reportMolecule}_report.html`)
    
    // $: console.log(includePlotsInReport, includeTablesInReports)
    let reportTitle = "", reportComments = "", reportMethod = "info", reportMolecule = "", reportCount = 0
    let reportTitleContents = "", loadContent = "";
    const stylesheet = path.resolve(__dirname, 'assets/reports/template.css')

    const getHTMLContent = (content) =>{

        return (
            `<!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset='utf8'>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <meta http-equiv="X-UA-Compatible" content="ie=edge">
                    <title>${reportMolecule} Reports</title>
                    <link rel="stylesheet" type='text/css' href="report_stylesheet.css">
                </head>

                <body>
                    <section class="section" id="mainSection">
                        <div class="content">
                            <h1 id="mainTitle">${reportMolecule}</h1>
                            ${content}
                        </div>
                    </section>
                </body>
            </html>`

        )

    }

    function getImage(imgID) {
        return new Promise(resolve => {

            Plotly.toImage(imgID, {format: 'png', width: 1000, height: 500}).then(dataURL =>{resolve(dataURL)})
        });
    }
    
    const exprtToHtml = async (content) => {
        fs.writeFile(reportFile, content, function(err) {

            if(err) {
                createToast("Report couldn't be added.", "danger")
                return console.log(err);
            }
            console.log("The file was saved!");
            createToast("Report added", "success")

            let local_cssFile = path.resolve(currentLocation, 'reports/report_stylesheet.css')
        
            if (!fs.existsSync(local_cssFile)){
                fs.copyFile(stylesheet, local_cssFile, (err) => {
                    if (err) throw err;
                    console.log('template.css file copied');
                });
            }
            console.log("Exported to HTML")
        })

    }

    const addReport = async() => {

        let reportDir = path.resolve(currentLocation, "reports")
        if (!fs.existsSync(reportDir)) {fs.mkdirSync(reportDir); console.log("reports directory created")}

        reportCount++
        if (reportTitle.length == 0) reportTitle = `Title-${reportCount}`
        if (reportComments.length == 0) reportComments = "-"
        
        let tableData=[], imgList_HTML = []

        includeTablesInReports.forEach(tb=>{

            if(tb.include) {
                let tableContent;
                try {
                    tableContent = document.getElementById(tb.id).innerHTML
                } catch (error) {
                    createToast(`${tb.label} is not visible`, "danger")
                }
            tableData = [...tableData, `<h1 class="title">${tb.label}</h1>\n<table class='table is-bordered is-hoverable'>${tableContent}</table>\n`]
            }
        })

        let index = 0
        
        await asyncForEach(includePlotsInReport, async (plot)=>{
            if (plot.include) {
                console.log("Request Image URL for ", plot.id)
                let imgURL = await getImage(plot.id)

                console.log(`Received Image URL for ${plot.id}\n`)
                imgList_HTML = [...imgList_HTML, `<img id='img-${plot.id}' src='${imgURL}'>`]

                console.log(`${plot.id} Included in HTML`)
            }
            index++
        })
        console.log("Combining HTML to write")
        reportTitleContents += `\n<div class="content"><h1 class="notification is-${reportMethod}">${reportTitle}</h1>\n` 
            + marked(reportComments)
            + imgList_HTML.toString()
            + tableData.toString()
            + "\n<hr></div>\n"

        loadContent = getHTMLContent(reportTitleContents)
        reportComments = reportTitle = ""

        exprtToHtml(loadContent)
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
                            if (error) {$modalContent = error; $activated = true; return}
                            createToast('Write PDF successfully.', "success")
                        })
                    }).catch(error => { $modalContent = error; $activated = true })

                } else {
                    reportWindow.webContents.printToPDF({printBackground: true, landscape:landscape, pageSize:pageSize}, (error, data) => {
                        if(error) { $modalContent = error; $activated = true; return}
                        fs.writeFile(reportFile.replace(".html", ".pdf"), data, (error) => {
                            if (error) {$modalContent = error; $activated = true; return}
                            createToast('Write PDF successfully.', "success")
                        })
                    })
                }
            }
        })
        
    }


    const notificationMethod = [{name:"info", color:"white"}, {name:"success", color:"#00ff00"}, {name:"warning", color:"yellow"}, {name:"danger", color:"red"}]

</script>

<style>

    .notification { margin-top: 1em; border: 1px solid; }

    .button {margin-right: 1em;}


    .report {display: flex; align-items: inherit; flex-direction: column;}
    .addToReport > hr {margin: auto; width: 50%;}
    .addToReport > h1 {margin: 5px 0; justify-content: center; display: flex;}
    .addToReport > div {margin: 1em 0; justify-content: center; display: flex; flex-wrap: wrap;}
</style>

<div class="title notification is-link">Add to report</div>
<div style="margin-bottom:1em;">
    <Textfield style="height:3em; width:20em;" variant="outlined" bind:value={reportMolecule} label="Molecule Name" />
    <button class="button is-pulled-right is-warning" on:click="{()=>{reportTitleContents=""; reportCount=0; createToast("Resetted", "warning")}}">Reset Report</button>
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
        NOTE: You can write in markdown format (eg: # Title, ## Subtilte, **bold**, _italics_, > BlockQuotes, >> Nested BlockQuotes,  1., 2. for list, etc.,)
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