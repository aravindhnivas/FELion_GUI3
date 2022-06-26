<script>
    import { felixOutputName, felixopoLocation } from '../../functions/svelteWritables'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import { createEventDispatcher } from 'svelte'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    export let writeFile
    export let writeFileName = 'average_normline.dat'
    export let output_namelists
    export let overwrite_expfit
    const dispatch = createEventDispatcher()
</script>

<div class="align">
    <CustomSelect bind:value={$felixOutputName} label="Output filename" options={output_namelists} />
    <TextAndSelectOptsToggler
        toggle={false}
        bind:value={writeFileName}
        label="writeFileName"
        lookIn={window.path.resolve($felixopoLocation, '../EXPORT')}
        lookFor=".dat"
        autoUpdate={true}
        auto_init={true}
    />
    <CustomSwitch style="margin: 0 1em;" bind:selected={writeFile} label="Write" />
    <CustomSwitch style="margin: 0 1em;" bind:selected={overwrite_expfit} label="Overwrite" />
    <button class="button is-link" on:click={() => dispatch('addfile')}>Add files</button>
    <button class="button is-link" on:click={() => dispatch('removefile')}>Remove files</button>
</div>
