
<script>

    import Radio from '@smui/radio'
    import FormField from '@smui/form-field'
    import CustomCheckbox from './CustomCheckbox.svelte'
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index'
    import Ripple from '@smui/ripple'
    import {createToast} from "./Layout.svelte"
    const {BrowserWindow} = remote


    export let currentLocation = "", id="report", plotID = [], tableID="felixTable", includeTable=false
    $: reportFile = path.resolve(currentLocation, `${reportMolecule}_report.html`)
    let extra_plotInclude = _.fill(Array(plotID.length), false)

    $: console.log(extra_plotInclude, plotID)
    
    let reportTitle = "", reportComments = "", reportMethod = "info", reportMolecule = "", reportCount = 0
    let include_table = includeTable, include_plot = true
    
    let reportTitleContents = "", loadContent = "";
    localStorage["reportStyle"] = path.resolve(__dirname, 'assets/reports/template.css')

    const getHTMLContent = (content) =>{
        return (
            `<!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset='utf8'>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <meta http-equiv="X-UA-Compatible" content="ie=edge">
                    <title>${reportMolecule} Reports</title>
                    <link rel="stylesheet" href="${localStorage["reportStyle"]}">
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

    async function asyncForEach(array, callback) {
        for (let index = 0; index < array.length; index++) {
            await callback(array[index], index, array);
        }
    }


    function getImage(imgID) {
        return new Promise(resolve => {
            html2canvas(document.getElementById(imgID)).then(canvasElm =>{resolve(canvasElm.toDataURL())})
        });

    }
    
    const addReport = async() => {

        reportCount++
        if (reportTitle.length == 0) reportTitle = `Title-${reportCount}`
        if (reportComments.length == 0) reportComments = "-"
        
        let tableData, imgList_HTML = []
        
        include_table ? tableData = `<table class='table is-bordered is-hoverable'>${document.getElementById(tableID).innerHTML}</table>` : tableData = "\n"

        index = 0

        await asyncForEach(extra_plotInclude, async (value)=>{
            if (value) {
                console.log("Request Image URL for ", plotID[index])
                let imgURL = await getImage(plotID[index])
                console.log(`Received Image URL for ${plotID[index]}\n`, imgURL)
                
                imgList_HTML = [...imgList_HTML, `<img id='img-${plotID[index]}' src='${imgURL}'>`]

                console.log(`${plotID[index]} Included in HTML`)
            }
            index++

        })

        console.log("Combining HTML to write")
        reportTitleContents += `\n<h1 class="notification is-${reportMethod}">${reportTitle}</h1>\n` 
            + marked(reportComments)
            + imgList_HTML.toString()
            + tableData
            + "\n<hr>\n"

        loadContent = getHTMLContent(reportTitleContents)
        reportComments = reportTitle = ""
        
        fs.writeFile(reportFile, loadContent, function(err) {
            if(err) {
                createToast("Report couldn't be added.", "danger")
                return console.log(err);
            }
            console.log("The file was saved!");
            createToast("Report added", "success")
        });
    }
    
    const showReport = () => {
        let reportWindow = new BrowserWindow({ width: 1200, minWidth :600, height: 600, parent: remote.getCurrentWindow()})
        reportWindow.on('closed', () => { reportWindow = null; console.log("Report window closed") })

        reportWindow.loadURL(reportFile)
        reportWindow.webContents.on('did-finish-load', ()=>{ console.log("Report loaded") });
    
    }

</script>


<div class=""><h1 class="mdc-typography--headline4">Add to report</h1></div>
<hr>

<div style="margin-bottom:1em;">
    <Textfield style="height:3em; width:20em;" variant="outlined" bind:value={reportMolecule} label="Molecule Name" />
</div>

<div class="align report" {id} >
    {#each [{name:"info", color:"white"}, {name:"success", color:"#00ff00"}, {name:"warning", color:"yellow"}, {name:"danger", color:"red"}] as method}
        <FormField >
            <Radio bind:group={reportMethod} value={method.name}  />
            <span slot="label" style="color:{method.color}">{method.name}</span>
        </FormField>
    {/each}

    {#if includeTable}
        <CustomCheckbox bind:selected={include_table} label={"Include table"}/>
    {/if}
    
    {#each plotID as ID, index}
        <CustomCheckbox bind:selected={extra_plotInclude[index]} label={ID}/>
    {/each}
    <Textfield style="height:3em; margin-bottom:1em;" variant="outlined" bind:value={reportTitle} label="Title" />
    <Textfield textarea bind:value={reportComments} label="Comments"  
        input$aria-controls="{id}_comments" input$aria-describedby="{id}_comments"/>
    <HelperText id="{id}_comments">
        NOTE: You can write in markdown format (eg: # Title, **bold**, __italics__, 1., 2. for list, etc.,)
    </HelperText>

    <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click={addReport}>Add to Report</button>
    <button class="button is-link" use:Ripple={[true, {color: 'primary'}]} tabindex="0" on:click={showReport}>Show Report</button>
</div>