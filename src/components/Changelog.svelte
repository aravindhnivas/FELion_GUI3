
<script>
    import Modal from "./Modal.svelte";
    import {beforeUpdate} from "svelte";
    export let active=false;

    let changelogContent = fs.readFileSync(path.resolve(__dirname, "../CHANGELOG.md")).toString()
    
    beforeUpdate(()=>{changelogContent = fs.readFileSync(path.resolve(__dirname, "../CHANGELOG.md")).toString()})

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

{#if active}
    <Modal title="FELion GUI Changelog" bind:active>

        <div slot="content">{@html window.marked(changelogContent)}</div>
    </Modal>
{/if}