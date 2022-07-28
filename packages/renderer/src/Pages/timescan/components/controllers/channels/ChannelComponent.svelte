<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import Textfield from '@smui/textfield'
    // import type { LossChannel } from 'types/types'
    import { isUndefined } from 'lodash-es'

    export let item: Timescan.LossChannel
    export let rateConstantMode = false
    export let ions_lists: string[] = []

    const dispatch = createEventDispatcher()
</script>

<div class="channel_div">
    <i class="material-symbols-outlined">menu</i>
    <CustomSelect bind:value={item.type} label="type" options={['forwards', 'backwards']} />
    <Textfield bind:value={item.name} label="name" />
    <CustomSelect bind:value={item.lossFrom} label="lossFrom" options={['<resp. ion>', ...ions_lists]} />
    <CustomSelect
        bind:value={item.attachTo}
        label="attachTo"
        options={['none', 'all', ...ions_lists.filter((n) => n !== item.lossFrom)]}
    />
    {#if item.sliderController}
        <Textfield bind:value={item.sliderController} label="(min, max, step)" style="width: 10em;" />
    {/if}
    {#if rateConstantMode && !isUndefined(item.numberDensity)}
        <Textfield bind:value={item.numberDensity} label="He^n" style="width: 7em;" />
    {/if}
    <button
        class="button is-danger"
        on:click={() => {
            dispatch('remove', { id: item.id })
        }}>X</button
    >
</div>

<style>
    .channel_div {
        display: flex;
        justify-content: space-evenly;
        align-items: flex-end;
        gap: 1em;
    }
    i {
        cursor: move;
    }
</style>
