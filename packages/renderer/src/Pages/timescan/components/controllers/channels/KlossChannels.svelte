<script lang="ts">
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import FileReadAndLoad from '$components/FileReadAndLoad.svelte'
    import ChannelComponent from './ChannelComponent.svelte'
    import { onMount } from 'svelte'
    import { differenceBy, find } from 'lodash-es'
    import Textfield from '@smui/textfield'
    import default_channels, { get_slider_controller, base_slider_values_str } from './default_channels'

    import type { loss_channelsType } from '$src/Pages/timescan/types/types'

    import CustomPanel from '$components/CustomPanel.svelte'

    export let loss_channels: loss_channelsType[] = []
    export let nameOfReactants = ''
    export let rateConstantMode = false

    export let configDir: string = ''
    export let useTaggedFile: boolean = false
    export let tagFile: string = ''
    export let selectedFile: string = ''

    let channelCounter = 0
    let maxGuess = '0.5'
    $: ions_lists = nameOfReactants.split(',').map((name) => name.trim())
    $: if (selectedFile) {
        defaultMode = false
    }
    const addChannel = () => {
        loss_channels = [
            {
                type: 'forwards',
                name: channelCounter > 0 ? `k_loss_${channelCounter}` : 'k_loss',
                lossFrom: ions_lists[0],
                attachTo: 'none',
                id: window.getID(),
                numberDensity: '',
                sliderController: base_slider_values_str(maxGuess),
            },
            ...loss_channels,
        ]
        channelCounter += 1
    }
    const ktrap_loss_channel = {
        type: 'forwards',
        name: 'ktrap_loss',
        lossFrom: '<resp. ion>',
        attachTo: 'none',
        id: window.getID(),
        numberDensity: '',
        sliderController: base_slider_values_str(maxGuess),
    }
    const updateTrapLossChannel = () => {
        const channelFound = find(loss_channels, ktrap_loss_channel)
        console.log(find(loss_channels, ktrap_loss_channel))
        if (channelFound) return window.createToast('channel already added', 'warning')
        loss_channels = [ktrap_loss_channel, ...loss_channels]
    }

    // $: if (loss_channels?.length === 0) {
    //     channelCounter = 0
    // }

    let defaultMode = false

    $: nameOfReactantsArr = nameOfReactants.split(',').map((n) => n.trim())
    let defaultChannelsArr: loss_channelsType[]

    const make_default_channels = (event?: CustomEvent) => {
        if (!defaultMode) {
            loss_channels = differenceBy(loss_channels, defaultChannelsArr, 'id')
            return
        }
        defaultChannelsArr = default_channels(nameOfReactantsArr, rateConstantMode, maxGuess)
        loss_channels = [...loss_channels, ...defaultChannelsArr]
    }

    onMount(() => {
        loss_channels = []

        make_default_channels()
    })

    const trigger_rateConstantMode_change = () => {
        loss_channels = loss_channels.map((channel) => {
            const number_density_exponent = parseInt(channel?.numberDensity?.split('^')[1])
            if (!isNaN(number_density_exponent)) {
                if (rateConstantMode) {
                    channel.sliderController = get_slider_controller(number_density_exponent)
                } else {
                    channel.sliderController = base_slider_values_str(maxGuess)
                }
            }
            return channel
        })
    }

    let channels_file = 'kinetics.channels.json'

    const updateGuessMaxValues = () => {
        loss_channels = loss_channels.map((channel) => {
            channel.sliderController = base_slider_values_str(maxGuess)
            return channel
        })
    }

    let data_loaded = false
</script>

<CustomPanel loaded={data_loaded} label="Channels" style="display: flex; flex-direction: column;">
    <FileReadAndLoad
        bind:filename={channels_file}
        bind:dataToSave={loss_channels}
        bind:data_loaded
        options_filter=".channels.json"
        {...{
            configDir,
            selectedFile,
            tagFile,
            useTaggedFile,
        }}
    />
    <div class="align h-center">
        <button class="button is-link" on:click={addChannel}>Add channel</button>
        <button class="button is-warning" on:click={updateTrapLossChannel}>Add trap loss channel</button>
        <CustomSwitch bind:selected={defaultMode} label="He-attachment mode" on:change={make_default_channels} />
        <CustomSwitch
            bind:selected={rateConstantMode}
            label="rateConstant mode"
            on:change={trigger_rateConstantMode_change}
        />
    </div>

    <div class="align h-center mb-5">
        {#if !rateConstantMode}
            <Textfield bind:value={maxGuess} label="max-guess-value" />
            <i class="material-icons" on:click={updateGuessMaxValues}>refresh</i>
        {/if}
    </div>

    <div class="channels_div mb-5">
        {#each loss_channels as item (item.id)}
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
</CustomPanel>

<style langs="scss">
    .channels_div {
        display: flex;
        flex-direction: column;
        row-gap: 1rem;
        overflow: auto;

        padding: 0 1em;
        width: 100%;
    }
</style>
