<script lang="ts">
    import { Panel, Header, Content } from '@smui-extra/accordion'
    import IconButton, { Icon } from '@smui/icon-button'

    export let open = false
    export let label: string = 'label'
    export let style: string = ''
    let className: string = ''
    export { className as class }
    export let loaded: boolean = true
    $: console.log(`loaded ${loaded}: ${label}`)
</script>

<Panel bind:open style="background: var(--color-primary-light);">
    <Header>
        <div class="align">
            <IconButton pressed={loaded}>
                <Icon class="material-symbols-outlined">sync_problem</Icon>
                <Icon class="material-symbols-outlined" on>done</Icon>
            </IconButton>
            {label}
        </div>
        <IconButton slot="icon" toggle pressed={open}>
            <Icon class="material-symbols-outlined" on>expand_less</Icon>
            <Icon class="material-symbols-outlined">expand_more</Icon>
        </IconButton>
    </Header>
    <Content class={className} style="{style}; border-top: solid 1px;">
        <slot />
    </Content>
</Panel>
