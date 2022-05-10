<script context="module">
    import CustomCheckbox from '$src/components/CustomCheckbox.svelte'
    import CustomTextSwitch from '$src/components/CustomTextSwitch.svelte'
    export const components = {
        Textfield: CustomTextSwitch,
        Checkbox: CustomCheckbox,
    }
</script>
