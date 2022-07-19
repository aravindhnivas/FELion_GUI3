<script>
    import Textfield from '@smui/textfield'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    export let defaultInitialValues = true
    export let initialValues = ''
    // export let ratek3 = ''
    // export let k3Guess = ''
    // export let ratekCID = ''
    // export let kCIDGuess = ''
    export let kinetics_fitfile = ''
    export let configDir = ''
</script>

<div class="align h-center">
    <CustomSwitch bind:selected={defaultInitialValues} label="default" />
    <Textfield bind:value={initialValues} label="initialValues" />
    <!-- <Textfield bind:value={ratek3} label="ratek3" />
    <Textfield bind:value={k3Guess} label="k3Guess (min, max, step)" />
    <Textfield bind:value={ratekCID} label="ratekCID" />
    <Textfield bind:value={kCIDGuess} label="kCIDGuess (min, max, step)" /> -->
    <TextAndSelectOptsToggler
        bind:value={kinetics_fitfile}
        label="fit-config file (*.fit.json)"
        lookFor=".fit.json"
        lookIn={configDir}
    />
</div>
