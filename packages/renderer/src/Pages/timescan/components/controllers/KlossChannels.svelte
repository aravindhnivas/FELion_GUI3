<script>
    import Textfield from '@smui/textfield'
    import CustomSelect from '$components/CustomSelect.svelte'
    import { createEventDispatcher } from 'svelte'
    export let loss_channels = []
    export let nameOfReactants = ''
    const addChannel = () => {
        loss_channels = [
            ...loss_channels,
            { type: 'forwards', name: 'k_loss', attachTo: 'none', id: getID() },
        ]
    }

    // const dispatch = createEventDispatcher()
    const channelAdded = (e, channel) => {
        console.log(channel)
        const add_or_update = e.target.textContent
        if (add_or_update.toLowerCase() === 'add') {
            e.target.textContent = 'Added'
            // dispatch('add', { channel })
        } else {
            e.target.textContent = 'updated'
            // dispatch('update', { channel })
        }
        e.target.disabled = true
        setTimeout(() => {
            e.target.textContent = 'update'
            e.target.disabled = false
        }, 500)
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
                        bind:value={channel.attachTo}
                        label="attachTo"
                        options={[
                            'none',
                            ...nameOfReactants
                                .split(',')
                                .map((name) => name.trim()),
                        ]}
                    />
                    <button
                        class="button is-link"
                        on:click={(e) => channelAdded(e, channel)}>ADD</button
                    >
                    <button
                        class="button is-danger"
                        on:click={() => {
                            loss_channels = loss_channels.filter(
                                (c) => c.id !== channel.id
                            )
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
        min-height: 150px;
        max-height: 60%;
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
