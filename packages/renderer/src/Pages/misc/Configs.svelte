<script>
    import Textfield from '@smui/textfield';
    import { onDestroy } from 'svelte';
    export let active = ''
    let CONFIGS = db?.data() || {}

    const unsubscribe = window.db.onDidAnyChange((newValue, oldValue) => {
        CONFIGS = newValue
    })
    onDestroy(unsubscribe)
    
</script>

<div class="config_main__div box" style:display={active == 'Configs' ? 'grid' : 'none'}>
    <Textfield
    style="border: solid 1px #fff7;"
        value={window.db.path}
        label="CONFIGS location"
        disabled
        />
        <div class="config__div ">
            {#each Object.keys(CONFIGS) as label}
            <div class="config_content">
                <Textfield bind:value={CONFIGS[label]} {label} />
                <button
                class="button is-success"
                on:click={() =>
                        window.db.set(label, CONFIGS[label])}
                    >Save</button
                >
                <button
                class="button is-warning"
                on:click={() => window.db.delete(label)}
                >Clear</button
                >
            </div>
            {:else}
            <h1>No data</h1>
        {/each}
    </div>
    
    <div class="config_footer" style="margin-left: auto;">
        <button
        class="button is-danger"
        on:click={() => window.db.clear()}>Clear all</button
        >
    </div>
</div>

<style lang="scss">
    .config_main__div {
        display: grid;
        grid-template-rows: auto 1fr auto;
        max-height: calc(100vh - 15rem);
        gap: 1em;
        .config__div {
            display: grid;
            overflow: auto;

            padding-right: 1em;
            gap: 1em;
            .config_content {
                display: grid;
                grid-auto-flow: column;
                grid-template-columns: 1fr auto;
                align-items: baseline;
                gap: 1em;
            }
        }
    }
</style>