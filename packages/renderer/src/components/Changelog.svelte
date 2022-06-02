<script>
    import { activateChangelog } from '../js/functions'
    import Modal from '$components/modal/Modal.svelte'
    import SvelteMarkdown from 'svelte-markdown'

    const changelogFile = pathJoin(ROOT_DIR, 'resources/CHANGELOG.md')
    let source = window.fs.readFileSync(changelogFile)
    $: if (env.DEV && $activateChangelog) {
        console.log('reading changelog')
        source = window.fs.readFileSync(changelogFile)
    }
</script>

{#if $activateChangelog}
    <Modal
        bind:active={$activateChangelog}
        id="changelog"
        class="changelog__container"
        title="FELion GUI Changelog"
        content$style="user-select:text;"
    >
        <svelte:fragment slot="content">
            <SvelteMarkdown {source} />
        </svelte:fragment>
    </Modal>
{/if}
