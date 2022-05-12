<script>
    import Textfield from '@smui/textfield'
    import TextAndSwitchToggler from '$src/components/TextAndSwitchToggler.svelte'
    import CustomSwitch from '$src/components/CustomSwitch.svelte'

    export let defaultInitialValues = true
    export let initialValues = ''

    export let include_loss_channel = false

    export let ratek3 = ''
    export let k3Guess = ''

    export let ratekCID = ''
    export let kCIDGuess = ''

    export let config_filelists = []
    export let kinetics_fitfile = ''
    export let readConfigDir = () => {}

    const update_loss_channel = () => {
        if (ratek3.includes('k_loss')) {
            return (loss_channel_status = 'already included')
        }
        if (!include_loss_channel) return
        ratek3 += ratek3.trim().endsWith(',') ? 'k_loss' : ', k_loss'
        loss_channel_status = 'added'
    }

    let loss_channel_status = ''
</script>

<div class="box column">
    <div>
        <CustomSwitch
            bind:selected={defaultInitialValues}
            label="defaultInitialValues"
        />
        <Textfield bind:value={initialValues} label="initialValues" />
    </div>
    <div>
        <CustomSwitch
            bind:selected={include_loss_channel}
            label="loss channel"
            on:SMUISwitch:change={update_loss_channel}
        />
        {#if loss_channel_status}
            <span class="tag">{loss_channel_status}</span>
        {/if}

        <Textfield
            bind:value={ratek3}
            label="ratek3"
            on:change={() => {
                if (ratek3.includes('k_loss')) {
                    loss_channel_status = 'loss channel added'
                    include_loss_channel = true
                } else {
                    include_loss_channel = false
                    loss_channel_status = 'loss channel removed'
                }
            }}
        />
        <Textfield bind:value={k3Guess} label="k3Guess (min, max) [/s]" />
    </div>

    <div>
        <Textfield bind:value={ratekCID} label="ratekCID" />
        <Textfield bind:value={kCIDGuess} label="kCIDGuess (min, max) [/s]" />
    </div>

    <TextAndSwitchToggler
        bind:value={kinetics_fitfile}
        label="fit-config file (*.fit.json)"
        options={config_filelists.filter((f) => f.endsWith('.fit.json'))}
        update={readConfigDir}
    />
</div>

<style lang="scss">
    .column {
        display: flex;
        gap: 1rem;
        justify-content: center;
        div {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
    }

    .box {
        margin: 0;
        padding: 0.5em;
        border: solid 1px #fff7;
    }
</style>
