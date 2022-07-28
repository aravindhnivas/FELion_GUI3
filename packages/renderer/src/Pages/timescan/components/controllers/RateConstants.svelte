<script lang="ts">
    import Textfield from '@smui/textfield'
    import TextAndSelectOptsToggler from '$components/TextAndSelectOptsToggler.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'

    export let defaultInitialValues = true
    export let initialValues = ''
    export let kinetics_fitfile = ''
    export let configDir = ''
</script>

<div class="align h-center">
    <CustomSwitch bind:selected={defaultInitialValues} label="default" />
    <Textfield bind:value={initialValues} label="initialValues" />
    <TextAndSelectOptsToggler
        bind:value={kinetics_fitfile}
        label="fit-config file (*.fit.json)"
        lookFor=".fit.json"
        lookIn={configDir}
    />
</div>
