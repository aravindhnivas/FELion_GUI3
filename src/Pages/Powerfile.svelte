<script>
    
    // Importing modules
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index';
    import Fab, {Icon, Label} from '@smui/fab';
    import Checkbox from '@smui/checkbox';
    import FormField from '@smui/form-field';
    import {createToast, browse} from "../components/Layout.svelte"
    import {modalContent, activated} from "../components/Modal.svelte"

    //////////////////////////////////////////////////////////////////////////////////

    function savefile() {

        if (location.length == 0) {return createToast("Location is not set. Browse folder to set location", "danger")}

        console.log('Powerfile contents saving')

        let powfile = path.resolve(location, `${filename}.pow`)
        if (fs.existsSync(powfile)){
            createToast("Powerfile overwritten to existing file", "warning")
        }

        let contents = `${initContent}\n${powerfileContent}`
        fs.writeFile(powfile, contents , function(err) {
            if(err) {

                createToast("Power file couldn't be saved.", "danger")
                return console.log(err);
            }
            createToast("Power file saved", "success")
        })
    }

    function openFolder() {

        browse({dir:true}).then(result=>{
            if (!result.canceled) {
                location = localStorage["powerfile_location"] = result.filePaths[0]
                createToast("Location updated", "success")
            }
        }).catch(err=>{$modalContent = err; $activated=true})

    }

    let powerfileContent = '', felixHz = 10, felixShots = 16, convert = null;
    let location = localStorage["powerfile_location"] || "";

    let today = new Date();
    const dd = String(today.getDate()).padStart(2, '0')
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const yy = today.getFullYear().toString().substr(2)
    let filename = `${dd}_${mm}_${yy}-#`;

    $: conversion = "_no_"
    $: convert ? conversion = "_" : conversion = "_no_"

    $: initContent = `#POWER file\n` +
        `# ${felixHz} Hz FELIX\n` +
        `#SHOTS=${felixShots}\n` +
        `#INTERP=linear\n` +
        `#    IN${conversion}UM (if one deletes the no the firs number will be in \mu m\n` +
        `# wavelength/cm-1      energy/pulse/mJ\n`

</script>

<style>

    .section {height: 70vh;}
    .container { height: 100%; margin-bottom: 3em; }
    @media only screen and (max-height: 800px) {.section {overflow-y: auto;}}

</style>

<section class="section" id="Powerfile" style="display:none">
    <div class="container" id="powfileContainer">

        <div style="margin-bottom:2em;">
            <Textfield  style="width:90%" bind:value={location} label="Current Location" />
            <Fab class="is-pulled-right" on:click={openFolder} extended><Label>Browse</Label></Fab>
        </div>

        <div style="margin-bottom:2em;">
            <Textfield style="width:20%" bind:value={filename} label="Filename" />
            <Textfield style="width:20%" bind:value={felixShots} label="FELIX Shots" on:change={()=>{console.log(felixShots)}}/>
            <Textfield style="width:20%" bind:value={felixHz} label="FELIX Hz" />
            <FormField>
                <Checkbox bind:checked={convert} indeterminate={convert === null} />
                <span slot="label">Convert to &micro;m</span>
            </FormField>
        </div>

        <Textfield textarea bind:value={powerfileContent} label="Powerfile contents" 
            input$aria-controls="powercontent_help" input$aria-describedby="powercontent_help"/>
        <HelperText id="powercontent_help">Enter powerfile measured for {filename}.felix file (wavenumber power-in mJ)</HelperText>
        <Fab style="margin:2em 0;" on:click={savefile} extended><Label>Save</Label></Fab>
    
    </div>
</section>