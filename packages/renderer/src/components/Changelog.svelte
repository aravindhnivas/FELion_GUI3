
<script>
    import {windowLoaded, activateChangelog, updateAvailable, newVersion, updating} from "../js/functions";
    import Modal from "./Modal.svelte";
    import { beforeUpdate} from "svelte";
    import { Remarkable } from 'remarkable';
    import { fade } from 'svelte/transition';

    const changelogFile = pathJoin(ROOT_DIR, "resources/CHANGELOG.md")
    let changelogContent = fs.readFileSync(changelogFile)
    const md = new Remarkable();
    beforeUpdate(()=>{changelogContent = fs.readFileSync(changelogFile)})
    
    const updateEvent = new CustomEvent('update', { bubbles: false });


    const updateNow = () => {
        
        let target = document.getElementById("updateCheckBtn")

        target.dispatchEvent(updateEvent)
    }

    let changelogTitle = "FELion GUI Changelog"
    $: if($updateAvailable) {
        $activateChangelog = true;
        changelogTitle = "New update available: "+ $newVersion
    
    } else {changelogTitle = "FELion GUI Changelog"}

</script>


{#if $activateChangelog && $windowLoaded}

    <Modal title={changelogTitle} bind:active={$activateChangelog}>
        <div slot="content" transition:fade style="user-select:text;">
            {#if $updateAvailable && window.changelogNewContent}

                {@html md.render(window.changelogNewContent)}
            {:else}
                {@html md.render(changelogContent)}
            {/if}
        
        </div>

        <div slot="footerbtn">
            {#if $updateAvailable}
                <button class="button is-warning" class:is-loading={$updating} on:click={updateNow}>Update Now</button>

            {/if}
        </div>

    </Modal>

{/if}

{@html `<style>

    ul {padding-left: 1em;}

    li {list-style: disc;}

    h1 {
        color: #fafafa;
        font-size: 2rem;
        font-weight: 600;
        line-height: 1.125;
    }

    h2 {

        color: #fafafa;
        font-size: 1.25rem;
        font-weight: 400;
        line-height: 1.25;
    }


    h1, h2 {

        word-break: break-word;
        margin-bottom: 0.5em;
    }


</style>`}