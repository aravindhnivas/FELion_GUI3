<script>
    import { toggleRow, felixopoLocation, normMethod } from '../../functions/svelteWritables'
    import { theory_func } from '../../functions/theory'
    // import { fade } from 'svelte/transition'
    import CustomTextSwitch from '$components/CustomTextSwitch.svelte'
    import QuickBrowser from '$components/QuickBrowser.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    /////////////////////////////////////////////////////////////////////////

    // export let normMethod
    export let theoryLocation
    // export let show_theoryplot

    let sigma = 7
    let scale = 1
    let tkplot = false
    let theoryfiles = []
    let showTheoryFiles = false
    let theoryfilesChecked = []

    $: if (window.fs.isDirectory(theoryLocation)) {
        theoryfiles = theoryfilesChecked.map((file) => window.path.resolve(theoryLocation, file))
    }

    async function plotData(e = null) {
        const pyfile = 'normline.theory'

        if (theoryfiles.length < 1) return window.createToast('No files selected', 'danger')

        const args = {
            theoryfiles,
            normMethod: $normMethod,
            sigma,
            scale,
            currentLocation: $felixopoLocation,
            tkplot,
            onlyExpRange,
        }

        const dataFromPython = await computePy_func({ e, pyfile, args })
        if (!dataFromPython) return
        theory_func({ dataFromPython, normMethod })
        // window.createToast("Graph Plotted", "success")
        showTheoryFiles = false
    }

    let onlyExpRange = false
    $: if (theoryLocation) {
        window.db.set('theoryLocation', theoryLocation)
    }
</script>

<QuickBrowser
    title="Theory files"
    bind:active={showTheoryFiles}
    bind:currentLocation={theoryLocation}
    bind:fileChecked={theoryfilesChecked}
    on:submit={(e) => {
        plotData(e.detail.event)
    }}
/>

{#if $toggleRow}
    <BrowseTextfield
        class="two_col_browse box"
        style="border: solid 1px;"
        bind:value={theoryLocation}
        label="Theory location"
    />

    {#if window.fs.isDirectory(theoryLocation)}
        <div class="align">
            <button
                class="button is-warning"
                on:click={() => {
                    showTheoryFiles = !showTheoryFiles
                }}>Show File</button
            >
            <CustomTextSwitch style="width:7em;" variant="outlined" bind:value={sigma} label="Sigma" step="0.5" />
            <CustomTextSwitch
                style="width:7em"
                variant="outlined"
                bind:value={scale}
                label="Scale"
                step="0.001"
                max="1"
            />
            <CustomSwitch style="margin: 0 1em;" bind:selected={onlyExpRange} label="Only Exp. Range" />
            <CustomSwitch style="margin: 0 1em;" bind:selected={tkplot} label="Matplotlib" />
            <button class="button is-link" on:click={plotData}>Replot</button>
        </div>
    {/if}
{/if}
