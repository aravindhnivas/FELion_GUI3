<script>

    import Paper, {Title as Title1, Subtitle, Content} from '@smui/paper';
    import Slider from '@smui/slider';
    import Radio from '@smui/radio';
    import {onMount} from "svelte"
    export let elevation = 6;

    import LoremIpsum from "../testing/LoremIpsum.svelte"
    let color = 'default';
    export let id="";

    
</script>

<style>
    /* .paper-container {margin: 2em;} */
</style>

<section class="paper-container" {id} style="display:none">
    <Paper class="paper-demo" color="primary" {elevation}>
        <Title1>{id}</Title1>
        <Subtitle>This is a sheet of paper.</Subtitle>
        <Content>Paper is used to build an elevated surface.</Content>
    </Paper>
    <!-- <LoremIpsum n={12}/> -->
</section>