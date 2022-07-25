<script lang="ts">
    import {
        pyVersion,
        pythonpath,
        pythonscript,
        pyServerPORT,
        developerMode,
        pyServerReady,
        felionpy,
    } from './settings/svelteWritables'
    import { updateInterval } from '$src/sveltewritables'
    import { activateChangelog } from '../js/functions'
    import { getPyVersion, resetPyConfig } from './settings/checkPython'
    import Textfield from '@smui/textfield'
    import { onMount, onDestroy } from 'svelte'
    import Changelog from '$components/Changelog.svelte'
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import { checkTCP, fetchServerROOT } from './settings/serverConnections'
    import { Unsubscribe } from 'conf/dist/source/types'
    import { browse } from '$src/components/Layout.svelte'
    import IconButton from '$components/IconButton.svelte'

    let pyError = ''
    let updateError = <string>window.db.get('updateError') || ''
    let updateIntervalCycle: NodeJS.Timer | null = null
    const selected = window.persistentDB('settingsActiveTab', 'Configuration')
    let unsubscribers: Unsubscribe[] = []

    unsubscribers[0] = window.db.onDidChange('pyServerReady', async (value: boolean) => {
        $pyServerReady = value
        if ($pyServerReady) {
            serverInfo += `>> fetching server status\n`
            await updateServerInfo()
        }
    })

    unsubscribers[1] = window.db.onDidChange('updateError', (err: string) => {
        updateError = err
    })

    unsubscribers[2] = window.db.onDidChange('delayupdate', (delay: number) => {
        if (delay) {
            if (updateIntervalCycle) {
                clearInterval(updateIntervalCycle)
            }

            setTimeout(() => {
                updateCheck()
                updateIntervalCycle = setInterval(updateCheck, $updateInterval * 60 * 1000)
            }, 60 * 60 * 1000)
        }
    })
    onMount(async () => {
        try {
            if (!$pyVersion) {
                console.warn('python is invalid. computing again')
                await getPyVersion()
                console.warn($pyVersion)
            }
            $pyServerReady = <boolean>window.db.get('pyServerReady')
        } catch (error) {
            pyError = String(error)
        } finally {
            serverInfo += `>> pyVersion: ${$pyVersion}\n`
            if ($pyServerReady) {
                await updateServerInfo()
            }
            if (import.meta.env.DEV) return
            updateIntervalCycle = setInterval(updateCheck, $updateInterval * 60 * 1000)
        }
    })
    // console.log('meta', import.meta.env)
    let updating = false

    unsubscribers[3] = window.db.onDidChange('update-status', (status) => {
        console.log(status)
        switch (status) {
            case 'checking-for-update':
                updating = true
                break

            case 'update-not-available':
                updating = false
                break

            case 'download-error':
                updating = false
                break

            case 'update-downloaded':
                updating = false
                break

            default:
                break
        }
    })

    function updateCheck(event = null) {
        if (import.meta.env.DEV) return console.info('Cannot update in DEV mode')

        try {
            if (!navigator.onLine) {
                if (event) {
                    return window.createToast('No Internet Connection!', 'warning')
                }
            }
            window.checkupdate()
        } catch (error) {
            if (event && error instanceof Error) window.handleError(error)
        }
    }

    let serverInfo = ''

    const updateServerInfo = async (e: ButtonClickEvent = null) => {
        const rootpage = await fetchServerROOT({ target: e?.target })
        if (!rootpage.includes('ERROR')) {
            $pyServerReady = true
            serverInfo += `>> ${rootpage}\n`
            return
        }
    }

    const serverDebug = window.persistentDB('serverDebug', false)
    const updateTCPInfo = async (e = null) => {
        const [{ stdout }] = await checkTCP({ target: e?.target })
        if (stdout) {
            serverInfo += `>> ${stdout}\n`
        } else {
            serverInfo += `>> ERROR occured while checking TCP connection on port:${$pyServerPORT}\n`
        }
    }
    const tabs = ['Configuration', 'Update', 'About', 'Infos']
    let showServerControls = false

    onDestroy(() => {
        unsubscribers.forEach((unsubscribe) => unsubscribe())
        if (updateIntervalCycle) {
            clearInterval(updateIntervalCycle)
        }
    })

    let lock_felionpy_program = import.meta.env.PROD

    const id = 'Settings'
    let display = window.db.get('active_tab') === id ? 'block' : 'none'
</script>

<Changelog />

<section class="section animate__animated animate__fadeIn" {id} style="display:{display}">
    <div class="main__div">
        <div class="box interact left_container__div">
            <div class="title__div">
                {#each tabs as tab (tab)}
                    <div class="hvr-glow" class:clicked={$selected === tab} on:click={() => ($selected = tab)}>
                        {tab}
                    </div>
                {/each}
            </div>
        </div>

        <div class="mainContainer box">
            <div class="container right" id="Settings_right_column">
                <div class="align animate__animated animate__fadeIn" class:hide={$selected !== 'Configuration'}>
                    <h1>Configuration</h1>

                    <div class="align">
                        <div class="tag is-warning">
                            {$pyVersion || 'Python undefined'}
                        </div>
                        <div class="tag" class:is-danger={!$pyServerReady} class:is-success={$pyServerReady}>
                            {$pyServerReady ? `server running (port: ${$pyServerPORT})` : 'felionpy server closed'}
                        </div>

                        <div class="align">
                            <button
                                class="button is-link"
                                on:click={() => {
                                    $developerMode = !$developerMode
                                }}
                            >
                                Developer mode: {$developerMode}
                            </button>
                            <button class="button is-link" on:click={getPyVersion}>getPyVersion</button>

                            <button class="button is-link" on:click={() => (showServerControls = !showServerControls)}>
                                Show server controls
                            </button>

                            {#if $developerMode}
                                <div class="align">
                                    <Textfield bind:value={$pythonpath} label="Python path" style="width: 100%; " />
                                    <Textfield
                                        bind:value={$pythonscript}
                                        label="Python script path"
                                        style="width: 100%; "
                                    />
                                    <button class="button is-link" on:click={resetPyConfig}>Reset</button>
                                    <button
                                        class="button is-link"
                                        on:click={async () => {
                                            try {
                                                await getPyVersion()
                                            } catch (error) {
                                                if (error instanceof Error) window.handleError(error)
                                            }
                                        }}>Save</button
                                    >
                                </div>
                            {/if}
                        </div>

                        <!-- {#if import.meta.env.DEV} -->
                        <div class="browse__div">
                            <button
                                disabled={lock_felionpy_program}
                                class="button is-link"
                                on:click={async () => {
                                    const [result] = await browse({ dir: false })
                                    if (!result) return

                                    console.log(result)
                                    $felionpy = result
                                }}>Browse</button
                            >
                            <Textfield
                                disabled={lock_felionpy_program}
                                style="width: 100%;"
                                bind:value={$felionpy}
                                label="felionpy"
                            />

                            <IconButton bind:value={lock_felionpy_program} icons={{ on: 'lock', off: 'lock_open' }} />
                        </div>
                        <!-- {/if} -->

                        {#if pyError && !pyServerReady}
                            <div class="align tag is-danger errorbox">
                                {pyError}
                            </div>
                        {/if}

                        <div class="align server-control" class:hide={!showServerControls}>
                            <div class="align">
                                <Textfield disabled type="number" bind:value={$pyServerPORT} label="serverPORT" />
                                <CustomSwitch bind:selected={$serverDebug} label="serverDebug" />

                                <button class="button is-link" on:click={window.startServer} disabled={$pyServerReady}>
                                    STARTserver
                                </button>

                                {#if $pyServerReady}
                                    <button class="button is-danger" on:click={window.stopServer}> STOPserver </button>
                                {/if}

                                <button class="button is-warning" on:click={updateTCPInfo}>Check TCP</button>
                            </div>

                            <div class="align">
                                <button id="fetchServerROOT" class="button is-link" on:click={updateServerInfo}
                                    >fetchServerROOT</button
                                >
                                <button
                                    class="button is-danger"
                                    on:click={() => {
                                        serverInfo = ''
                                    }}>Clear</button
                                >
                            </div>
                        </div>

                        <div class="serverContainer align box">
                            {serverInfo}
                        </div>
                    </div>
                </div>

                <div class="align animate__animated animate__fadeIn" class:hide={$selected !== 'Update'}>
                    <h1 class="title">Update</h1>

                    <div class="subtitle" style="width: 100%;">
                        App Version {window.appVersion}
                    </div>
                    <div class="align">
                        <div class="align">
                            <button
                                class="button is-link"
                                class:is-loading={updating}
                                id="updateCheckBtn"
                                on:click={updateCheck}>Check update</button
                            >
                            <button
                                class="button is-warning"
                                on:click={() => {
                                    $activateChangelog = true
                                }}>What's New</button
                            >
                        </div>

                        <div id="update-progress-container" style="display: none;">
                            <label for="file">Download progress:</label>
                            <progress id="update-progress" max="100" value="0"> 0%</progress>
                        </div>

                        {#if updateError}
                            <div class="tag is-danger errorbox animate__animated animate__fadeIn">
                                {updateError}
                            </div>
                        {/if}
                    </div>
                </div>

                <div class="animate__animated animate__fadeIn" class:hide={$selected !== 'About'}>
                    <h1 class="title">About</h1>
                    <div class="content">
                        <ul style="user-select: text;">
                            <li>FELionGUI: {window.appVersion}</li>
                            <li>{$pyVersion}</li>
                            <hr />
                            {#each Object.keys(window.versions) as key}
                                <li>{key}: {window.versions[key]}</li>
                            {/each}
                        </ul>
                    </div>
                </div>

                <div class="animate__animated animate__fadeIn" class:hide={$selected !== 'Infos'}>
                    <h1 class="title">Infos</h1>
                    <div class="infos__div">
                        {#each Object.keys(window.appInfo) as label}
                            {@const value = window.appInfo[label]}
                            <div class="info__item">
                                <Textfield {value} {label} disabled />
                                <i class="material-icons" on:click={() => window.shell.showItemInFolder(value)}
                                    >open_in_new</i
                                >
                            </div>
                        {/each}
                    </div>
                </div>
            </div>
        </div>
    </div>
</section>

<style lang="scss">
    .browse__div {
        display: grid;
        grid-auto-flow: column;
        align-items: center;
        gap: 1em;
        grid-template-columns: auto 1fr auto;
        width: 100%;
    }
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
            text-align: center;
            cursor: pointer;
            display: grid;
            row-gap: 2em;
            div {
                font-size: 22px;
            }
        }

        #update-progress-container {
            progress {
                width: 100%;
            }
            display: grid;
            width: 100%;
            gap: 1em;
            grid-template-columns: auto 1fr;
            align-items: center;
        }
    }

    h1 {
        margin: 0;
        width: 100%;
    }

    .errorbox {
        white-space: pre-line;
        height: 100%;
        width: fit-content;
        font-size: medium;
        margin-left: auto;
        border: solid 1px;
    }

    .mainContainer {
        overflow: auto;
    }

    .serverContainer {
        overflow: auto;
        user-select: text;
        white-space: pre-wrap;
        align-items: baseline;
        height: calc(42vh - 5rem);
        max-height: calc(42vh - 5rem);
    }
    .infos__div {
        display: flex;
        flex-direction: column;
        .info__item {
            display: grid;
            grid-auto-flow: column;
            grid-template-columns: 1fr auto;
        }
    }
</style>
