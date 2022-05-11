<script>
    import Textfield from '@smui/textfield'
    import CustomSelect from '$src/components/CustomSelect.svelte'
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
        console.log('update_loss_channel')
        if (!include_loss_channel || ratek3.includes('k_loss')) return
        if (ratek3.trim().endsWith(',')) ratek3 += 'k_loss'
        else ratek3 += ', k_loss'
    }
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
        <Textfield bind:value={ratek3} label="ratek3" />
        <Textfield bind:value={k3Guess} label="k3Guess (min, max) [/s]" />
    </div>
    <div>
        <Textfield bind:value={ratekCID} label="ratekCID" />
        <Textfield bind:value={kCIDGuess} label="kCIDGuess (min, max) [/s]" />
    </div>

    <div>
        <CustomSelect
            bind:value={kinetics_fitfile}
            label="fit-config file (*.fit.json)"
            options={config_filelists.filter((file) =>
                file.endsWith('.fit.json')
            )}
            update={readConfigDir}
        />
    </div>
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
