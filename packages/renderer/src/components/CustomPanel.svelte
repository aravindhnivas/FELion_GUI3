<script lang="ts">
    import { Panel, Header, Content } from '@smui-extra/accordion'
    import IconButton, { Icon } from '@smui/icon-button'

    export let open = false
    export let label: string = 'label'
    export let style: string = ''
    export let loaded: boolean = true

    $: console.log(`loaded ${label}`)
    const panelStyle = 'background: var(--color-primary-light);'
</script>

<Panel bind:open style={panelStyle}>
    <Header>
        <div class="align">
            <IconButton toggle pressed={loaded}>
                <Icon class="material-icons">sync_problem</Icon>
                <Icon class="material-icons" on>done</Icon>
            </IconButton>
            {label}
        </div>
        <IconButton slot="icon" toggle pressed={open}>
            <Icon class="material-icons" on>expand_less</Icon>
            <Icon class="material-icons">expand_more</Icon>
        </IconButton>
    </Header>
    <Content style="{style}; border-top: solid 1px;">
        <slot />
    </Content>
</Panel>
