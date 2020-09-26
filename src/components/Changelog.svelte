
<script>
    import {windowLoaded, activateChangelog} from "../js/functions";
    import Modal from "./Modal.svelte";
    import {onMount, beforeUpdate} from "svelte";
    import { fade } from 'svelte/transition';
    let changelogContent = fs.readFileSync(path.resolve(__dirname, "../CHANGELOG.md")).toString()
    
    beforeUpdate(()=>{changelogContent = fs.readFileSync(path.resolve(__dirname, "../CHANGELOG.md")).toString()})
    onMount(()=> {if(localStorage.showUpdate) {$activateChangelog = true; localStorage.showUpdate = ""}})

</script>

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

{#if $activateChangelog && $windowLoaded}

    <Modal title="FELion GUI Changelog" bind:active={$activateChangelog}>
        <div slot="content" transition:fade style="user-select:text;">{@html window.marked(changelogContent)}</div>

    </Modal>

{/if}