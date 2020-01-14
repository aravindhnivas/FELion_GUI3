<script>

    // import Paper, {Title as Title1, Subtitle, Content} from '@smui/paper';
    import Slider from '@smui/slider';
    import Radio from '@smui/radio';
    // export let elevation = 0;

    let color = 'default';
    export let id="";

    import TopAppBar, {Row, Section, Title as Title1} from '@smui/top-app-bar';
    import IconButton from '@smui/icon-button';
    import Checkbox from '@smui/checkbox';
    import FormField from '@smui/form-field';
    import LoremIpsum from './LoremIpsum.svelte';
    let prominent = false;
    let dense = false;
    let secondaryColor = false;

    import Drawer from './Drawer.svelte';
    
    let current = 'main';
    let drawer;
    let drawerOpen = false;

    function go(key) {
        current = key;
        drawerOpen = false;
    }
</script>

<style>
    /* .paper-container {margin-top: 2em} */
    /* .paper-demo {height: 70vh;} */

</style>

<section class="paper-container" {id} style="display:none">
    <!-- <Paper class="paper-demo" color="primary" {elevation}>
        <Title1>{id}</Title1>
        <Subtitle>This is a sheet of paper.</Subtitle>
        <Content>Paper is used to build an elevated surface.</Content>
    </Paper> -->

  <h2>Top App Bar</h2>

  <div>
    <FormField>
      <Checkbox bind:checked={prominent} />
      <span slot="label">Prominent</span>
    </FormField>
    <FormField>
      <Checkbox bind:checked={dense} />
      <span slot="label">Dense</span>
    </FormField>
    <FormField>
      <Checkbox bind:checked={secondaryColor} />
      <span slot="label">Secondary</span>
    </FormField>
  </div>

  <div class="flexy">
    <div class="top-app-bar-container flexor">
      <TopAppBar variant="fixed" {prominent} {dense} color={secondaryColor ? 'secondary' : 'primary'}>
        <Row>
          <Section>
            <IconButton class="material-icons">menu</IconButton>
            <Title1>Flex Static</Title1>
          </Section>
          <Section align="end" toolbar>
            <IconButton class="material-icons" aria-label="Download">file_download</IconButton>
            <IconButton class="material-icons" aria-label="Print this page">print</IconButton>
            <IconButton class="material-icons" aria-label="Bookmark this page">bookmark</IconButton>
          </Section>
        </Row>
      </TopAppBar>
        <div class="flexor-content"> <Drawer /> </div>
      
    </div>
  </div>
</section>