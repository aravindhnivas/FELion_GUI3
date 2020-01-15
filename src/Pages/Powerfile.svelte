<script>
    
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text/index';
    import Fab, {Icon, Label} from '@smui/fab';
    import Checkbox from '@smui/checkbox';
    import FormField from '@smui/form-field';
    
    function savefile() {
        console.log('Powerfile contents saving');
        let message = SnackBar({
            message: "File saved!",
            status: "success",
            container: "powfileContainer"
        });

}
    let filename = '';
    let powerfileContent = '';
    let felixHz = 10;
    let felixShots = 16;
    let convert = null;
    let location = localStorage["powerfile_location"] || "";
    $: console.log("Powerfile convert: ", convert)
</script>

<style>

    .section {height: 70vh;}
    
    .container {
        height: 100%;
        margin-bottom: 3em;
    }

    @media only screen
    and (max-height: 800px) {
        .section {overflow-y: auto;}
    }
</style>

<section class="section" id="Powerfile" style="display:none">
    <div class="container" id="powfileContainer">

        <div style="margin-bottom:2em;">
            <Textfield  style="width:90%" bind:value={location} label="Current Location" />
            <Fab class="is-pulled-right" on:click={savefile} extended><Label>Browse</Label></Fab>
        </div>

        <div style="margin-bottom:2em;">
            <Textfield variant="outlined" style="width:20%" bind:value={filename} label="Filename" />        
            <Textfield variant="outlined" style="width:20%" bind:value={felixShots} label="FELIX Shots" on:change={()=>{console.log(felixShots)}}/>
            <Textfield variant="outlined" style="width:20%" bind:value={felixHz} label="FELIX Hz" />
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