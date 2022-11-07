<script>
    import { currentTab } from '../svelteWritables'
    import Textfield from '@smui/textfield'
</script>

<div class="animate__animated animate__fadeIn" class:hide={$currentTab !== 'Infos'}>
    <h1>Infos</h1>
    <div class="infos__div">
        {#each Object.keys(window.appInfo) as label}
            {@const value = window.appInfo[label]}
            <div class="info__item">
                <Textfield {value} {label} disabled />

                <i
                    role="presentation"
                    class="material-symbols-outlined"
                    on:click={() => window.shell.showItemInFolder(value)}>open_in_new</i
                >
            </div>
        {/each}
    </div>
</div>

<style lang="scss">
    .infos__div {
        display: flex;
        flex-direction: column;
        .info__item {
            display: grid;
            grid-auto-flow: column;
            grid-template-columns: 1fr auto;
            align-items: flex-end;
        }
    }
</style>
