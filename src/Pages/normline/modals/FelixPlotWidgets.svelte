

<script>
    import CustomCheckList from '../../../components/CustomCheckList.svelte';
    import Textfield from '@smui/textfield';
    import CustomCheckbox from '../../../components/CustomCheckbox.svelte';
    import { createEventDispatcher } from 'svelte';

    export let felixPlotCheckboxes, felixPlotWidgets;

    const dispatch = createEventDispatcher();


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

</style>

<div class="">

    <div style="display:flex; flex-wrap:wrap;">

        {#each felixPlotCheckboxes as {label, options, selected, style, id}(id)}
            <div style="flex-grow:1; {style}" class="felix_tkplot_filelist_div">
                <div class="subtitle felix_tkplot_filelist_header">{label}</div>
                <CustomCheckList style="background: #836ac05c; border-radius: 20px; margin:1em 0;  height:20em; overflow:auto;" bind:fileChecked={selected} bind:items={options} />

            </div>
        {/each}
    </div>

    <div class="felix_plotting_div">

        <h1 class="subtitle">Text Widgets</h1>
        <div class="widgets">

            {#each felixPlotWidgets.text as {label, value, id}(id)}

                <Textfield style="width:12em; margin-bottom:1em;" variant="outlined" type="text" bind:value {label}/>

            {/each}

        </div>
        <button class="button is-link" on:click="{()=>{dispatch("addWidget", {type:"text"})}}">Add widget</button>

    </div>

    <div class="felix_plotting_div">

        <h1 class="subtitle">Number Widgets</h1>
        <div class="widgets">
            {#each felixPlotWidgets.number as {label, value, step, id}(id)}
                <Textfield style="width:12em; margin-bottom:1em;" type="number" {step} bind:value {label}/>

            {/each}
        </div>
        <button class="button is-link" on:click="{()=>{dispatch("addWidget", {type:"number"})}}">Add widget</button>

    </div>

    <div class="felix_plotting_div">
    
        <h1 class="subtitle">Boolean Widgets</h1>
        <div class="widgets">
            {#each felixPlotWidgets.boolean as {label, value, id}(id)}
                <CustomCheckbox style="width:12em; margin-bottom:1em;" bind:selected={value} {label} />
            {/each}
        </div>
        <button class="button is-link" on:click="{()=>{dispatch("addWidget", {type:"boolean"})}}">Add widget</button>
    </div>

</div>