<script lang="ts">
    import Accordion, { Panel, Header, Content } from '@smui-extra/accordion'
    import IconButton, { Icon } from '@smui/icon-button'
    let panel1Open = false
    let panel2Open = false
</script>

<Accordion multiple style="width: 100%;">
    <Panel bind:open={panel1Open} style="background: var(--color-primary);">
        <Header>
            Panel 1
            <IconButton slot="icon" toggle pressed={panel1Open}>
                <Icon class="material-icons" on>expand_less</Icon>
                <Icon class="material-icons">expand_more</Icon>
            </IconButton>
        </Header>
        <Content>The content for panel 1.</Content>
    </Panel>
    <Panel bind:open={panel2Open} style="background: var(--color-primary);">
        <Header>
            Panel 2
            <IconButton slot="icon" toggle pressed={panel2Open}>
                <Icon class="material-icons" on>expand_less</Icon>
                <Icon class="material-icons">expand_more</Icon>
            </IconButton>
        </Header>
        <Content>The content for panel 2.</Content>
    </Panel>
</Accordion>
