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
    // let updateBackgroundColor = ''

    let display = window.db.get('active_tab') === id ? 'block' : 'none'
    let navbarBadgeSettings: HTMLElement
    let updateBadge: HTMLElement
    let configBadge: HTMLElement

    onMount(() => {
        updateBadge = document.getElementById(`settings-badge-Update`)
        configBadge = document.getElementById(`settings-badge-Configuration`)
        navbarBadgeSettings = document.getElementById(`navbar-badge-${id}`)
    })

    onDestroy(() => {
        navbarBadgeSettings.style.backgroundColor = ''
    })

    const warningStatuses = [false, false]
    const updateSettingStatus = async () => {
        const status = warningStatuses.every((element) => element === false)
        navbarBadgeSettings.style.backgroundColor = status ? '' : 'var(--color-danger)'
    }
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
                        <Badge id="settings-badge-{tab}" style="min-height: 10px; min-width: 10px; padding: 0;" />
                    </div>
                {/each}
            </div>
        </div>

        <div class="mainContainer box">
            <div class="container right">
                <Configuration
                    on:serverStatusChanged={({ detail: { closed } }) => {
                        console.log('server closed', closed)
                        configBadge.style.backgroundColor = closed ? 'var(--color-danger)' : ''
                        warningStatuses[0] = closed
                        updateSettingStatus()
                    }}
                />
                <Update
                    on:updateStatusChange={(e) => {
                        warningStatuses[1] = false
                        if (!e.detail.status) return
                        updateBadge.style.backgroundColor = 'var(--color-danger)'
                        warningStatuses[1] = true
                        updateSettingStatus()
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
