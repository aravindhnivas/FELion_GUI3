
<script>
    import Modal from "./Modal.svelte";
    import {onMount, beforeUpdate} from "svelte";
    import { fade } from 'svelte/transition';
    import {windowLoaded} from "../js/functions";
    export let active=false;

    let changelogContent = fs.readFileSync(path.resolve(__dirname, "../CHANGELOG.md")).toString()
    
    beforeUpdate(()=>{changelogContent = fs.readFileSync(path.resolve(__dirname, "../CHANGELOG.md")).toString()})
    onMount(()=> {if(localStorage.showUpdate) {active = true; localStorage.showUpdate = ""}})

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

{#if active && windowLoaded}
    <Modal title="FELion GUI Changelog" bind:active>

        <div slot="content" transition:fade style="user-select:text;">{@html window.marked(changelogContent)}</div>
    </Modal>
{/if}