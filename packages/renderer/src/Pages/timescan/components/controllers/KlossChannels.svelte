<script lang="ts">
    import Textfield from '@smui/textfield'
    import CustomSelect from '$components/CustomSelect.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import type { loss_channelsType } from '$src/Pages/timescan/types/types'
    import { persistentWritable } from '$src/js/persistentStore'
    import { onMount } from 'svelte'
    import { differenceBy } from 'lodash-es'
    import { resizableDiv } from '$src/js/resizableDiv.js'
    export let loss_channels: loss_channelsType = []
    export let nameOfReactants = ''
    export let includeTrapLoss = false

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
            },
        ]
        channelCounter += 1
    }
    $: if (loss_channels.length === 0) {
        channelCounter = 0
    }
    let defaultMode = persistentWritable('kinetics:defaultLossChannels', false)

    $: nameOfReactantsArr = nameOfReactants.split(',').map((n) => n.trim())
    let defaultChannels: loss_channelsType

    const make_default_channels = (event?: CustomEvent) => {
        if (!$defaultMode) {
            loss_channels = differenceBy(loss_channels, defaultChannels, 'id')
            return
        }

        console.log('making default channels')
        defaultChannels = []
        for (let i = 1; i < nameOfReactantsArr.length; i++) {
            const currention = nameOfReactantsArr[i - 1]
            const nextion = nameOfReactantsArr[i]

            const currentChannelForwards = {
                type: 'forwards',
                name: `k3${i}`,
                lossFrom: currention,
                attachTo: nextion,
                id: window.getID(),
            }

            const currentChannelBackwards = {
                type: 'backwards',
                name: `kCID${i}`,
                lossFrom: nextion,
                attachTo: currention,
                id: window.getID(),
            }
            defaultChannels = [...defaultChannels, currentChannelForwards, currentChannelBackwards]
        }
        loss_channels = [...loss_channels, ...defaultChannels]
    }

    onMount(() => {
        loss_channels = []
        make_default_channels()
        console.log($defaultMode)
        // if ($defaultMode) {
        //     make_default_channels(null)
        // }
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
        <CustomSwitch bind:selected={$defaultMode} label="He-attachment mode" on:change={make_default_channels} />
    </div>
    {#if loss_channels.length}
        <div class="channels_div">
            {#each loss_channels as channel (channel.id)}
                <div class="channel_div">
                    <CustomSelect bind:value={channel.type} label="type" options={['forwards', 'backwards']} />
                    <Textfield bind:value={channel.name} label="name" />
                    <CustomSelect bind:value={channel.lossFrom} label="lossFrom" options={ions_lists} />
                    <CustomSelect bind:value={channel.attachTo} label="attachTo" options={['none', ...ions_lists]} />

                    <button
                        class="button is-danger"
                        on:click={() => {
                            loss_channels = loss_channels.filter((c) => c.id !== channel.id)
                            channelCounter--
                        }}>X</button
                    >
                </div>
            {/each}
        </div>
    {/if}
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
    .channel_div {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        gap: 1em;
    }
    .box {
        max-height: 400px;
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
