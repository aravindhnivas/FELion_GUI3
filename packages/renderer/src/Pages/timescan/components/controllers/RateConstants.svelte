<script>
    import Textfield from '@smui/textfield'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomPanel from '$components/CustomPanel.svelte'

    export let defaultInitialValues = true
    export let initialValues = ''

    export let ratek3 = ''
    export let k3Guess = ''
    export let ratekCID = ''
    export let kCIDGuess = ''

    export let config_filelists = []
    export let kinetics_fitfile = ''

    export let readConfigDir = () => {}
</script>

<CustomPanel label="Initial values" style="display: flex; gap: 1em;">
    <div>
        <CustomSwitch bind:selected={defaultInitialValues} label="defaultInitialValues" />
        <Textfield bind:value={initialValues} label="initialValues" />
    </div>
    <div>
        <Textfield bind:value={ratek3} label="ratek3" />
        <Textfield bind:value={k3Guess} label="k3Guess (min, max, step)" />
    </div>

    <div>
        <Textfield bind:value={ratekCID} label="ratekCID" />
        <Textfield bind:value={kCIDGuess} label="kCIDGuess (min, max, step)" />
    </div>

    <TextAndSelectOptsToggler
        bind:value={kinetics_fitfile}
        label="fit-config file (*.fit.json)"
        options={config_filelists.filter((f) => f.endsWith('.fit.json'))}
        update={readConfigDir}
    />
</CustomPanel>

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
</style>
