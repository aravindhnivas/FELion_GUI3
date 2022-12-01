<script lang="ts">
    import SegmentedButton, { Segment, Label } from '@smui/segmented-button'
    export let choices: { name: string; selected: boolean }[] = []

    let className = ''
    export { className as class }
</script>

<SegmentedButton class={className} segments={choices} let:segment key={(segment) => segment.name}>
    <Segment
        {segment}
        selected={segment.selected}
        on:click={() => {
            segment.selected = !segment.selected
            choices = choices // Remember to do this so Svelte knows that `choices` has changed.
        }}
    >
        <Label>{segment.name}</Label>
    </Segment>
</SegmentedButton>

<style lang="scss" global>
    button.mdc-segmented-button__segment.mdc-ripple-upgraded {
        background-color: var(--color-primary);
        opacity: 0.7;
        &:hover {
            background-color: whitesmoke;
            .mdc-segmented-button__label {
                color: black;
            }
        }
        .mdc-segmented-button__label {
            color: white;
        }
        &.mdc-segmented-button__segment--selected {
            background-color: whitesmoke;
            opacity: 1;
            .mdc-segmented-button__label {
                color: black;
            }
        }
    }
</style>
