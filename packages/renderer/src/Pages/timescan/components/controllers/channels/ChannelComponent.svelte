<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    import CustomSelect from '$components/CustomSelect.svelte'
    import Textfield from '@smui/textfield'

    import type { loss_channelsType } from '$src/Pages/timescan/types/types'

    export let item: loss_channelsType
    export let ions_lists: string[] = []

    const dispatch = createEventDispatcher()
</script>

<div class="channel_div">
    <i class="material-icons">menu</i>
    <CustomSelect bind:value={item.type} label="type" options={['forwards', 'backwards']} />
    <Textfield bind:value={item.name} label="name" />
    <CustomSelect bind:value={item.lossFrom} label="lossFrom" options={ions_lists} />
    <CustomSelect bind:value={item.attachTo} label="attachTo" options={['none', ...ions_lists]} />
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
        justify-content: center;
        align-items: center;
        gap: 1em;
    }
    i {
        cursor: move;
    }
</style>
