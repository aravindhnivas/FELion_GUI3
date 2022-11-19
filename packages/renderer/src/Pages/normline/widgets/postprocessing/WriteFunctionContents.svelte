<script lang="ts">
    import { felixOutputName, felixopoLocation } from '../../functions/svelteWritables'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import { createEventDispatcher } from 'svelte'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'

    export let writeFile: boolean = false
    export let writeFileName = 'average_normline.dat'
    export let output_namelists: string[] = []
    export let overwrite_expfit: boolean = true

    const dispatch = createEventDispatcher()
    const uniqueID = getContext<string>('uniqueID')
    // $: console.warn($felixOutputName)
</script>

<div class="align">
    <CustomSelect bind:value={$felixOutputName[uniqueID]} label="Output filename" options={output_namelists} />
    <TextAndSelectOptsToggler
        toggle={false}
        bind:value={writeFileName}
        label="writeFileName"
        lookIn={window.path.resolve($felixopoLocation[uniqueID], '../EXPORT')}
        lookFor=".dat"
        auto_init={true}
    />
    <CustomSwitch style="margin: 0 1em;" bind:selected={writeFile} label="Write" />
    <CustomSwitch style="margin: 0 1em;" bind:selected={overwrite_expfit} label="Overwrite" />
    <button class="button is-link" on:click={() => dispatch('addfile')}>Add files</button>
    <button class="button is-link" on:click={() => dispatch('removefile')}>Remove files</button>
</div>
