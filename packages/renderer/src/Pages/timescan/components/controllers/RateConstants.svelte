<script>
    import Textfield from '@smui/textfield'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import CustomPanel from '$components/CustomPanel.svelte'

    export let defaultInitialValues = true
    export let initialValues = ''
    export let loaded = false
    export let ratek3 = ''
    export let k3Guess = ''
    export let ratekCID = ''
    export let kCIDGuess = ''

    // export let config_filelists = []
    export let kinetics_fitfile = ''

    export let configDir = ''
</script>

<CustomPanel label="Initial values" style="display: flex; gap: 1em; justify-content: center;" {loaded}>
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
        lookFor=".fit.json"
        lookIn={configDir}
    />
</CustomPanel>

<style>
    div {
        display: flex;
        flex-direction: column;
        gap: 1em;
    }
</style>
