<script>
    import { activateChangelog } from '../js/functions'
    import Dialog, { Title, Content, Actions } from '@smui/dialog'
    import Button, { Label } from '@smui/button'
    import SvelteMarkdown from 'svelte-markdown'
    const changelogFile = pathJoin(ROOT_DIR, 'resources/CHANGELOG.md')
    let source = fs.readFileSync(changelogFile)
    $: if (env.DEV && $activateChangelog) {
        console.log('reading changelog')
        source = fs.readFileSync(changelogFile)
    }
</script>

<Dialog
    bind:open={$activateChangelog}
    aria-labelledby="changelog-title"
    aria-describedby="changelog-content"
    surface$class="changelog__container"
    surface$style="max-width:50vw; max-height: 70vh;"
>
    <Title id="changelog-title">FELion GUI Changelog</Title>
    <Content id="changelog-content" style="user-select:text;">
        <SvelteMarkdown {source} />
    </Content>
    <Actions>
        <Button action="accept">
            <Label>Close</Label>
        </Button>
    </Actions>
</Dialog>
