<script>
    import Textfield from '@smui/textfield'
    import CustomSelect from '$components/CustomSelect.svelte'

    export let loss_channels = []
    export let nameOfReactants = ''
    $: ions_lists = nameOfReactants.split(',').map((name) => name.trim())
    let channelCounter = 0
    const addChannel = () => {
        loss_channels = [
            ...loss_channels,
            {
                type: 'forwards',
                name:
                    channelCounter > 0 ? `k_loss_${channelCounter}` : 'k_loss',
                lossFrom: ions_lists[0],
                attachTo: 'none',
                id: getID(),
            },
        ]
        channelCounter += 1
    }
    $: if (loss_channels.length === 0) {
        channelCounter = 0
    }
</script>

<div class="box channel_main__div">
    <button class="button is-link" on:click={addChannel}
        >Add new loss channel</button
    >
    {#if loss_channels.length}
        <div class="channels_div">
            {#each loss_channels as channel (channel.id)}
                <div class="channel_div">
                    <CustomSelect
                        bind:value={channel.type}
                        label="type"
                        options={['forwards', 'backwards']}
                    />
                    <Textfield bind:value={channel.name} label="name" />
                    <CustomSelect
                        bind:value={channel.lossFrom}
                        label="lossFrom"
                        options={ions_lists}
                    />
                    <CustomSelect
                        bind:value={channel.attachTo}
                        label="attachTo"
                        options={['none', ...ions_lists]}
                    />

                    <button
                        class="button is-danger"
                        on:click={() => {
                            loss_channels = loss_channels.filter(
                                (c) => c.id !== channel.id
                            )
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
        min-height: 180px;
        max-height: 180px;
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
