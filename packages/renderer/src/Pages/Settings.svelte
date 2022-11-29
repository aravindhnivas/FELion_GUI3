<script lang="ts">
    import { currentTab } from './settings/svelteWritables'
    import Changelog from '$components/Changelog.svelte'
    import Configuration from './settings/components/Configuration.svelte'
    import Infos from './settings/components/Infos.svelte'
    import About from './settings/components/About.svelte'
    import Update from './settings/components/Update.svelte'
    import Badge from '@smui-extra/badge'

    const tabs = ['Configuration', 'Update', 'About', 'Infos']
    const id = 'Settings'
    let updateBackgroundColor = ''

    let display = window.db.get('active_tab') === id ? 'block' : 'none'
    let navbarBadgeSettings: HTMLElement
    onMount(() => {
        navbarBadgeSettings = document.getElementById(`navbar-badge-${id}`)
        // navbarBadgeSettings.style.backgroundColor = 'var(--color-danger)'
    })
    onDestroy(() => {
        console.warn('Settings destroyed')
        navbarBadgeSettings.style.backgroundColor = ''
    })
</script>

<Changelog />

<section class="section animate__animated animate__fadeIn" {id} style="display:{display}">
    <div class="main__div">
        <div class="box interact left_container__div">
            <div class="title__div">
                {#each tabs as tab (tab)}
                    <div
                        role="presentation"
                        class="hvr-glow"
                        class:clicked={$currentTab === tab}
                        on:click={() => ($currentTab = tab)}
                    >
                        <span class="mr-3">{tab}</span>
                        {#if tab === 'Update'}
                            <Badge
                                aria-label="update-status-badge"
                                id="update-status-badge-id"
                                style="min-height: 10px; min-width: 10px; padding: 0; background: {updateBackgroundColor};"
                            />
                        {/if}
                    </div>
                {/each}
            </div>
        </div>

        <div class="mainContainer box">
            <div class="container right">
                <Configuration />
                <Update
                    on:updateStatusChange={(e) => {
                        if (!e.detail.status) return
                        updateBackgroundColor = 'var(--color-danger)'
                        navbarBadgeSettings.style.backgroundColor = updateBackgroundColor
                    }}
                />
                <About />
                <Infos />
            </div>
        </div>
    </div>
</section>

<style lang="scss">
    section {
        margin: 0;
        padding: 0;
    }
    .clicked {
        border-bottom: solid 1px;
    }
    .main__div {
        display: grid;
        grid-template-columns: 1fr 4fr;
        column-gap: 3em;
        height: calc(100vh - 7rem);

        .box {
            margin-bottom: 0px;
            border-radius: 0;
            background-color: #6a50ad8a;
        }

        .title__div {
            letter-spacing: 0.1em;
            text-transform: uppercase;
            // text-align: center;
            text-align: end;
            cursor: pointer;
            display: grid;
            row-gap: 2em;
            div {
                font-size: 22px;
            }
        }
    }
    .mainContainer {
        overflow: auto;
    }
</style>
