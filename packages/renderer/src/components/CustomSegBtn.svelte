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
