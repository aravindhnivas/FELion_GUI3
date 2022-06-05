<script lang="ts">
    // import Textfield from '@smui/textfield'
    // import CustomSelect from '$components/CustomSelect.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    // import { persistentWritable } from '$src/js/persistentStore'
    import ChannelComponent from './ChannelComponent.svelte'
    import { onMount } from 'svelte'
    import { differenceBy } from 'lodash-es'
    import { resizableDiv } from '$src/js/resizableDiv.js'
    // import SortableList from 'svelte-sortable-list'
    import default_channels from './default_channels'
    import type { loss_channelsType } from '$src/Pages/timescan/types/types'

    export let loss_channels: loss_channelsType[] = []
    export let nameOfReactants = ''
    export let includeTrapLoss = false
    export let rateConstantMode = false

    $: ions_lists = nameOfReactants.split(',').map((name) => name.trim())
    let channelCounter = 0

    const addChannel = () => {
        loss_channels = [
            ...loss_channels,
            {
                type: 'forwards',
                name: channelCounter > 0 ? `k_loss_${channelCounter}` : 'k_loss',
                lossFrom: ions_lists[0],
                attachTo: 'none',
                id: window.getID(),
                numberDensity: 'He^1',
            },
        ]
        channelCounter += 1
    }
    $: if (loss_channels.length === 0) {
        channelCounter = 0
    }
    let defaultMode = false

    $: nameOfReactantsArr = nameOfReactants.split(',').map((n) => n.trim())
    let defaultChannelsArr: loss_channelsType[]

    const make_default_channels = (event?: CustomEvent) => {
        if (!defaultMode) {
            loss_channels = differenceBy(loss_channels, defaultChannelsArr, 'id')
            return
        }
        defaultChannelsArr = default_channels(nameOfReactantsArr)
        loss_channels = [...loss_channels, ...defaultChannelsArr]
    }
    onMount(() => {
        loss_channels = []
        make_default_channels()
    })
</script>

<div
    class="box channel_main__div"
    use:resizableDiv={{
        change: { width: false, height: true },
        edges: { left: false, right: false, bottom: true, top: false },
    }}
>
    <div class="align h-center">
        <button class="button is-link" on:click={addChannel}>Add channel</button>
        <CustomSwitch bind:selected={includeTrapLoss} label="include trap losses (on all masses)" />
        <CustomSwitch bind:selected={defaultMode} label="He-attachment mode" on:change={make_default_channels} />
        <CustomSwitch bind:selected={rateConstantMode} label="rateConstant mode" />
    </div>
    <div class="channels_div">
        {#each loss_channels as item}
            <ChannelComponent
                {item}
                {rateConstantMode}
                {ions_lists}
                on:remove={(e) => {
                    const { id } = e.detail
                    loss_channels = loss_channels.filter((c) => c.id !== id)
                    channelCounter--
                }}
            />
        {/each}
    </div>
</div>

<style langs="scss">
    .channel_main__div {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .channels_div {
        overflow: auto;
        padding: 0 1em;
    }
    .box {
        max-height: 400px;
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
