<script lang="ts">
    import { felixPlotCheckboxes, theoryfiles, felixOpoDatfiles, theoryLocation } from '../functions/svelteWritables'
    import { fade } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import CustomCheckList from '$components/CustomCheckList.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    export let felixPlotWidgets: {
        text: ValueLabel<string>[]
        boolean: ValueLabel<boolean>[]
        number: ValueLabel<string>[]
    }

    async function loadFiles() {
        console.log($theoryfiles)
        $felixPlotCheckboxes = [
            {
                label: 'DAT_file',
                options: $felixOpoDatfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Fundamentals',
                options: $theoryfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Others',
                options: $theoryfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Overtones',
                options: $theoryfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Combinations',
                options: $theoryfiles,
                value: [],
                id: window.getID(),
            },
        ]
        console.log(`files loaded`)
    }
</script>

<div style="padding-bottom: 1em;">
    <div class="align mb-2">
        <BrowseTextfield class="two_col_browse" bind:value={$theoryLocation} label="Theory location" />
        <button class="button is-link ml-auto" on:click={loadFiles}>reload files</button>
    </div>
    <div class="align" style="justify-content: center;">
        {#each $felixPlotCheckboxes as { label, options, value, id } (id)}
            <div style="margin-bottom: 1em;" transition:fade>
                <div class="checkboxes_header">
                    {label}
                </div>
                <CustomCheckList class="modal_checkboxes__div" bind:fileChecked={value} bind:items={options} />
            </div>
        {/each}
    </div>

    <div class="felix_plotting_div">
        <div class="widgets">
            {#each felixPlotWidgets.text as { label, value, id } (id)}
                <Textfield type="text" bind:value {label} />
            {/each}
        </div>
        <div class="widgets">
            {#each felixPlotWidgets.number as { label, value, id } (id)}
                <Textfield type="text" bind:value {label} />
            {/each}
        </div>
        <div class="widgets">
            {#each felixPlotWidgets.boolean as { label, value, id } (id)}
                <CustomCheckbox bind:value {label} />
            {/each}
        </div>
    </div>
</div>

<style>
    .checkboxes_header {
        border: solid 1px white;
        width: 10em;
        padding: 0.2em;
        display: flex;
        justify-content: center;
        border-radius: 20px;
        margin: auto;
    }
    .felix_plotting_div {
        border: solid 1px white;
        border-radius: 20px;
        display: flex;
        flex-wrap: wrap;
        flex-direction: column;
        align-items: center;
    }

    .widgets {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5em;
        margin-bottom: 0.5em;
        justify-content: center;
    }
</style>
