<script lang="ts">
    import Badge from '@smui-extra/badge'
    export let type: string = 'link'
    export let style: string = ''
    export let id: string = window.getID()
    export let label: string = 'Submit'
</script>

<button {id} {style} class="button is-{type}" on:click on:pyEvent on:pyEventData on:pyEventStderr on:pyEventClosed>
    {label}<span class="material-icons"> double_arrow </span>
    <Badge><div id="{id}_badge" class="tag is-warning is-rounded mr-2" /></Badge>
</button>
