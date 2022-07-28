<script lang="ts">
    import { activateChangelog } from '../js/functions'
    import Modal from '$components/modal/Modal.svelte'
    import SvelteMarkdown from 'svelte-markdown'
    import { onMount } from 'svelte'

    const changelogFile = window.path.join(window.ROOT_DIR, 'resources/CHANGELOG.md')
    let source: string

    $: if (import.meta.env.DEV && $activateChangelog) {
        readChangelog()
    }

    const readChangelog = () => {
        const fileRead = window.fs.readFileSync(changelogFile)
        if (window.fs.isError(fileRead)) return window.handleError(fileRead)
        source = fileRead
    }
    onMount(readChangelog)
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
