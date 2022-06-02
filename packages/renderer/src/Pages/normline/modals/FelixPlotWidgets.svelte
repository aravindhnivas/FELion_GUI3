<script>
    import {
        felixopoLocation,
        felixPlotCheckboxes,
    } from '../functions/svelteWritables'
    import { fade } from 'svelte/transition'
    import Textfield from '@smui/textfield'
    import CustomCheckList from '$components/CustomCheckList.svelte'
    import CustomCheckbox from '$components/CustomCheckbox.svelte'

    export let felixPlotWidgets, theoryLocation

    let reload = true
    function refreshFunction() {
        const datlocation = window.path.resolve($felixopoLocation, '../EXPORT')
        const datfiles = window.fs.existsSync(datlocation)
            ? fs
                  .readdirSync(datlocation)
                  .filter((f) => f.endsWith('.dat'))
                  .map((f) => (f = { name: f, id: window.getID() }))
            : [{ name: '', id: window.getID() }]

        let calcfiles = []

        if (window.fs.existsSync(theoryLocation)) {
            window.fs.readdirSync(theoryLocation).forEach((file) => {
                const isFile = fs
                    .lstatSync(window.path.join(theoryLocation, file))
                    .isFile()
                if (isFile) {
                    calcfiles = [
                        ...calcfiles,
                        { name: file, id: window.getID() },
                    ]
                }
            })
        } else {
            calcfiles = [{ name: '', id: window.getID() }]
        }

        $felixPlotCheckboxes = [
            {
                label: 'DAT_file',
                options: datfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Fundamentals',
                options: calcfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Overtones',
                options: calcfiles,
                value: [],
                id: window.getID(),
            },
            {
                label: 'Combinations',
                options: calcfiles,
                value: [],
                id: window.getID(),
            },
        ]
        reload != reload
    }
</script>

<div style="padding-bottom: 1em;">
    <div>
        <button class="button is-link" on:click={refreshFunction}
            >load files</button
        >

        {#key reload}
            <div class="files__div">
                {#each $felixPlotCheckboxes as { label, options, value, id } (id)}
                    <div class="felix_tkplot_filelist_div" transition:fade>
                        <div class="subtitle felix_tkplot_filelist_header">
                            {label}
                        </div>
                        <CustomCheckList
                            style="background: #836ac05c; border-radius: 20px; margin:1em 0;  height:20em; overflow:auto;"
                            bind:fileChecked={value}
                            bind:items={options}
                        />
                    </div>
                {/each}
            </div>
        {/key}
    </div>

    <div class="felix_plotting_div">
        <h1 class="subtitle">Text Widgets</h1>

        <div class="widgets">
            {#each felixPlotWidgets.text as { label, value, id } (id)}
                <Textfield variant="outlined" type="text" bind:value {label} />
            {/each}
        </div>
    </div>
    <div class="felix_plotting_div">
        <h1 class="subtitle">Number Widgets</h1>
        <div class="widgets">
            {#each felixPlotWidgets.number as { label, value, step, id } (id)}
                <Textfield type="number" {step} bind:value {label} />
            {/each}
        </div>
    </div>

    <div class="felix_plotting_div">
        <h1 class="subtitle">Boolean Widgets</h1>
        <div class="widgets">
            {#each felixPlotWidgets.boolean as { label, value, id } (id)}
                <CustomCheckbox bind:value {label} />
            {/each}
        </div>
    </div>
</div>

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
        margin-bottom: 1em;
    }

    .felix_plotting_div {
        border: solid 1px white;
        border-radius: 20px;
        padding: 1em;
        display: flex;
        flex-wrap: wrap;
        flex-direction: column;
        align-items: center;
        margin: 1em 0;
    }

    .widgets {
        display: flex;
        flex-wrap: wrap;
        gap: 1em;
        margin-bottom: 1em;
        margin-top: 1em;
        justify-content: center;
    }
    .files__div {
        display: flex;
        gap: 1em;
        margin: 1em;
        flex-wrap: wrap;
    }
</style>
