<script>
    import { activateChangelog } from '../js/functions'
    import { Remarkable } from 'remarkable'
    import Dialog, { Title, Content, Actions } from '@smui/dialog'
    import Button, { Label } from '@smui/button'
    const changelogFile = pathJoin(ROOT_DIR, 'resources/CHANGELOG.md')
    let changelogContent = fs.readFileSync(changelogFile)
    const md = new Remarkable('default', {})
    const changelogTitle = 'FELion GUI Changelog'
    $: if ($activateChangelog) {
        changelogContent = fs.readFileSync(changelogFile)
    }
</script>

<Dialog
    bind:open={$activateChangelog}
    aria-labelledby="changelog-title"
    aria-describedby="changelog-content"
    surface$class="changelog__container"
    surface$style="max-width:50vw; max-height: 70vh;"
>
    <Title id="changelog-title">{changelogTitle}</Title>
    <Content id="changelog-content">
        {@html md.render(changelogContent)}
    </Content>
    <Actions>
        <Button action="accept">
            <Label>Close</Label>
        </Button>
    </Actions>
</Dialog>
