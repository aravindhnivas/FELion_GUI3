

<script>
    import {felixopoLocation, felixPlotCheckboxes} from '../functions/svelteWritables';
    import CustomCheckList from '$components/CustomCheckList.svelte';
    import Textfield from '@smui/textfield';
    import CustomCheckbox from '$components/CustomCheckbox.svelte';
    import { createEventDispatcher } from 'svelte';
    import { fade } from 'svelte/transition';

    export let felixPlotWidgets, theoryLocation;
    const dispatch = createEventDispatcher();

    let reload = false

    function refreshFunction() {

        // $felixPlotCheckboxes = []


        let datlocation = pathResolve($felixopoLocation, "../EXPORT")

        let datfiles = fs.existsSync(datlocation) ? fs.readdirSync(datlocation).filter(f=>f.endsWith(".dat")).map(f=>f={name:f, id:getID()}) : [{name:"", id:getID()}]
        let calcfiles = [];
        if(fs.existsSync(theoryLocation)) {
            fs.readdirSync(theoryLocation).forEach(file=>{
                const isfile = fs.lstatSync(pathJoin(theoryLocation, file)).isFile()
                if(isfile) {
                    calcfiles = [...calcfiles, {name:file, id:getID()}]
                }
            })
        } else {
            calcfiles = [{name:"", id:getID()}]
        }

        $felixPlotCheckboxes = [
                {label:"DAT file", options:datfiles, selected:[], id:getID()},
                {label:"Fundamentals", options:calcfiles, selected:[], id:getID()},
                {label:"Overtones", options:calcfiles, selected:[], id:getID()},
                {label:"Combinations", options:calcfiles, selected:[], id:getID()},
        ]
        // console.log($felixPlotCheckboxes)
        reload != reload

    }

</script>

<style>

    .felix_tkplot_filelist_header {
        border: solid 1px white;
        width: 10em;
        padding: 0.2em;
        display: flex;
        justify-content: center;
        border-radius: 20px;

        margin: auto;

    }
    .felix_tkplot_filelist_div {
        margin-bottom:1em;
    }


    .felix_plotting_div {
    
        border: solid 1px white;
        border-radius: 20px;
        padding: 1em;
        display: flex;
        flex-wrap: wrap;

        justify-content: center;
        margin: 1em 0;
    }

    .widgets {
        display: flex;
        flex-wrap: wrap;
        gap: 1em;
        margin-bottom: 1em;
        justify-content: center;
    }
    .files__div {
        display: flex;

        gap: 1em;
        margin: 1em;
        flex-wrap: wrap;
    
    }
</style>

<div style="padding-bottom: 1em;">

    <div >
        <button class="button is-link" on:click={refreshFunction}>Reload</button>

        {#key reload}

            <div class="files__div">
                {#each $felixPlotCheckboxes as {label, options, selected, id}(id)}

                    <div class="felix_tkplot_filelist_div" transition:fade>
                        <div class="subtitle felix_tkplot_filelist_header">{label}</div>
                        <CustomCheckList style="background: #836ac05c; border-radius: 20px; margin:1em 0;  height:20em; overflow:auto;" bind:fileChecked={selected} bind:items={options} />
                    </div>
                {/each}
            </div>
        {/key}

    </div>

    <div class="felix_plotting_div">
        <h1 class="subtitle">Text Widgets</h1>
        <div class="widgets">

            {#each felixPlotWidgets.text as {label, value, id}(id)}

                <Textfield variant="outlined" type="text" bind:value {label}/>

            {/each}

        </div>
        <button class="button is-link" on:click="{()=>{dispatch("addWidget", {type:"text"})}}">Add widget</button>

    </div>

    <div class="felix_plotting_div">

        <h1 class="subtitle">Number Widgets</h1>
        <div class="widgets">
            {#each felixPlotWidgets.number as {label, value, step, id}(id)}
                <Textfield type="number" {step} bind:value {label}/>

            {/each}
        </div>
        <button class="button is-link" on:click="{()=>{dispatch("addWidget", {type:"number"})}}">Add widget</button>

    </div>

    <div class="felix_plotting_div">
    
        <h1 class="subtitle">Boolean Widgets</h1>
        <div class="widgets">
            {#each felixPlotWidgets.boolean as {label, value, id}(id)}
                <CustomCheckbox bind:selected={value} {label} />
            {/each}
        </div>
        <button class="button is-link" on:click="{()=>{dispatch("addWidget", {type:"boolean"})}}">Add widget</button>
    </div>

</div>