<script>
  import Textfield from '@smui/textfield'
  import HelperText from '@smui/textfield/helper-text/index';
  import Fab, {Icon, Label} from '@smui/fab';

  function doSomething() {
    console.log('Powerfile contents: ', powerfileContent);
  }

  let filename = '';
  let powerfileContent = '';

</script>

<style>
    .section {height: 70vh;}
    .container {height: 100%;}
</style>

<section class="section" id="Powerfile" style="display:none">
    <div class="container">
        <Textfield variant="outlined" class="powfilename" bind:value={filename} label="Filename" />
        <Textfield class="powfilearea" textarea bind:value={powerfileContent} label="Powerfile contents" 
            input$aria-controls="powercontent_help" input$aria-describedby="powercontent_help"/>
        <HelperText id="powercontent_help">Helper Text</HelperText>
        <Fab on:click={doSomething} extended><Label>Save</Label></Fab>
    </div>
    
</section>