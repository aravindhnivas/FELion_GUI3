
<script>
    import {mainPreModal} from "../svelteWritable";
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index';
    import Checkbox from '@smui/checkbox';
    import FormField from '@smui/form-field';
    import {browse} from "../components/Layout.svelte";
    import CustomDialog from "../components/CustomDialog.svelte";

    const writePowfile = () => {
        let contents = `${initContent}\n${powerfileContent}`

        fs.writeFile(powfile, contents , function(err) {
            if(err) { return window.createToast("Power file couldn't be saved.", "danger") }
            window.createToast("Power file saved", "success")
        })
    }

    
    async function savefile() {
        if (location.length == 0) { return openFolder({save:true}) }
        const overwrite = await fs.existsSync(powfile)
        overwrite ? overwrite_dialog.open() : writePowfile()
    }

    function openFolder({save=false}={}) {
        browse({dir:true})
            .then(result=>{
                if (result) {
                    location = result[0]
                    db.set("powerfile_location", location)
                    window.createToast("Location updated", "success")
                    if (save) savefile()

                }
            
            }).catch(error=>{mainPreModal.error(error.stack || error)})
    
    }

    let powerfileContent = '', felixHz = 10, felixShots = 16, convert = null;


    let location = db.get("powerfile_location") || "";
    
    let overwrite_dialog;
    let today = new Date();

    const dd = String(today.getDate()).padStart(2, '0')
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const yy = today.getFullYear().toString().substr(2)

    let filename = `${dd}_${mm}_${yy}-#`;
    $: powfile = pathResolve(location, `${filename}.pow`)
    $: conversion = "_no_"
    $: convert ? conversion = "_" : conversion = "_no_"
    $: initContent = `#POWER file\n` +
        `# ${felixHz} Hz FELIX\n` +
        `#SHOTS=${felixShots}\n` +
        `#INTERP=linear\n` +

        `#    IN${conversion}UM (if one deletes the no the firs number will be in \mu m\n` +
        `# wavelength/cm-1      energy/pulse/mJ\n`

    

    const handleOverwrite = (e) => {
        let action = e.detail.action
        if (action === "Cancel" || action === "close") window.createToast("Powerfile saving cancelled", "warning")
        if (action === "Yes") writePowfile()
    }

</script>

<style>
    .section {max-height: 70vh;overflow-y: auto;}
    
    .main__container {
        display: grid; 
        height: 100%;

        grid-row-gap: 1em;
        margin: auto;
        width: 90%;
    }
    .grid_column__container {
        display: grid;
        grid-auto-flow: column;
        grid-column-gap: 1em;
    }

    .location__bar { display: flex; align-items: baseline; gap: 1em;}

    .file__details__bar {
        grid-template-columns: repeat(4, 1fr);
    }

    .power_value__container {
        display: grid;
        grid-template-rows: 12fr 1fr 2fr;
    }

</style>


<CustomDialog id="powerfile-overwrite" bind:dialog={overwrite_dialog} on:response={handleOverwrite}
    title={"Overwrite?"} content={`${filename} already exists. Do you want to overwrite it?`}/>
    

<section class="section" id="Powerfile" style="display:none">
    <div class="box main__container" id="powfileContainer">

        <div class="location__bar">
            <button class="button is-link" on:click={openFolder}>Browse</button>

            <Textfield  bind:value={location} label="Current Location" style="flex-grow:1;"/>
        
        </div>

        <div class="grid_column__container file__details__bar">
            <Textfield bind:value={filename} label="Filename" />

            <Textfield bind:value={felixShots} label="FELIX Shots" on:change={()=>{console.log(felixShots)}}/>

                <Textfield bind:value={felixHz} label="FELIX Hz" />

            <FormField>
                <Checkbox bind:checked={convert} indeterminate={convert === null} />

                <span slot="label">Convert to &micro;m</span>
            </FormField>


        </div>

        <div class="power_value__container">
            <Textfield textarea bind:value={powerfileContent} label="Powerfile contents" input$aria-controls="powercontent_help" input$aria-describedby="powercontent_help"/>

            <HelperText id="powercontent_help">Enter powerfile measured for {filename}.felix file (wavenumber power-in mJ)</HelperText>
            <button class="button is-success" style="width:12em;margin-left: auto;" on:click={savefile}>Save</button>
        </div>
        
    </div>
    
</section>