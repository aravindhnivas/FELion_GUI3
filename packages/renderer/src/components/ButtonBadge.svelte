<script lang="ts">
    import Badge from '@smui-extra/badge'
    export let className: string = 'is-link'
    export let style: string = ''
    export let id: string = window.getID()
</script>

<button {id} {style} class="button {className}" on:click>
    <slot />
    <Badge><div id="{id}_badge" class="tag is-warning is-rounded mr-2" /></Badge>
</button>
