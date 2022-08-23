<script lang="ts">
    import {
        pyVersion,
        pythonpath,
        pythonscript,
        pyServerPORT,
        developerMode,
        pyServerReady,
        felionpy,
        currentTab,
        serverDebug,
    } from '../svelteWritables'

    import BrowseTextfield from '$components/BrowseTextfield.svelte'
    import { getPyVersion } from '../checkPython'
    import { checkTCP, fetchServerROOT } from '../serverConnections'
    import CustomSwitch from '$src/components/CustomSwitch.svelte'
    import { onDestroy, onMount } from 'svelte'

    interface ServerInfo {
        value: string
        type: 'info' | 'danger' | 'warning' | 'success'
    }
    let showServerControls: boolean
    let serverInfo: ServerInfo[] = []
    let serverCurrentStatus: ServerInfo = { value: '', type: 'info' }

    const unsubscriber = window.db.onDidChange('pyServerReady', async (value) => {
        $pyServerReady = <boolean>value
        if ($pyServerReady) {
            serverInfo = [...serverInfo, { value: 'fetching server status', type: 'info' }]
            return await updateServerInfo()
        }
        serverCurrentStatus = { value: 'server closed', type: 'danger' }
        serverInfo = [...serverInfo, serverCurrentStatus]
    })

    const updateTCPInfo = async (e?: ButtonClickEvent) => {
        const target = e?.target as HTMLButtonElement
        const data = await checkTCP({ target })

        if (data instanceof Error) {
            serverInfo = [
                ...serverInfo,
                { value: `ERROR occured while checking TCP connection on port:${$pyServerPORT}\n`, type: 'danger' },
            ]
            return
        }
        serverInfo = [...serverInfo, { value: data.stdout, type: 'info' }]
    }

    const updateServerInfo = async (e?: ButtonClickEvent) => {
        serverCurrentStatus = { value: 'server starting...', type: 'info' }
        serverInfo = [...serverInfo, serverCurrentStatus]

        const target = e?.target as HTMLButtonElement
        const rootpage = await fetchServerROOT({ target })

        if (rootpage instanceof Error) {
            serverInfo = [...serverInfo, { value: rootpage.message, type: 'danger' }]
            serverCurrentStatus = { value: 'server closed', type: 'danger' }
        } else {
            $pyServerReady = true
            serverInfo = [...serverInfo, { value: rootpage, type: 'success' }]
            serverCurrentStatus = { value: `server running: port(${$pyServerPORT})`, type: 'success' }
            return
        }
    }

    onMount(async () => {
        try {
            if (!$pyVersion) {
                console.warn('python is invalid. computing again')
                await getPyVersion()
                console.warn($pyVersion)
            }
            $pyServerReady = <boolean>window.db.get('pyServerReady')
        } catch (error) {
            if (error instanceof Error) console.error(error)
        } finally {
            serverInfo = [...serverInfo, { value: `pyVersion: ${$pyVersion}`, type: 'info' }]
            if ($pyServerReady) {
                await updateServerInfo()
            }
        }
    })
    onDestroy(unsubscriber)
</script>

<div class="align animate__animated animate__fadeIn" class:hide={$currentTab !== 'Configuration'}>
    <h1>Configuration</h1>
    <div class="align">
        <div class="tag is-warning">
            {$pyVersion || 'Python undefined'}
        </div>
        <div class="tag is-{serverCurrentStatus.type}">
            {serverCurrentStatus.value}
        </div>

        <div class="align">
            <button class="button is-link" on:click={() => ($developerMode = !$developerMode)}>
                Developer mode: {$developerMode}
            </button>
            <button class="button is-link" on:click={getPyVersion}>getPyVersion</button>
            <button class="button is-link" on:click={() => (showServerControls = !showServerControls)}>
                Show server controls
            </button>

            {#if $developerMode}
                <div class="align">
                    <BrowseTextfield class="two_col_browse" bind:value={$pythonpath} label="pythonpath" dir={false} />
                    <BrowseTextfield class="two_col_browse" bind:value={$pythonscript} label="pythonscript" />
                    <button
                        class="button is-warning ml-auto"
                        on:click={async () => {
                            const output = await getPyVersion()
                            if (output instanceof Error) window.handleError(output)
                        }}>Save</button
                    >
                </div>
            {/if}
        </div>
        <BrowseTextfield class="three_col_browse" bind:value={$felionpy} label="felionpy" lock={true} />

        <div id="serverControllers" class="align server-control" class:hide={!showServerControls}>
            <div class="align">
                <BrowseTextfield
                    type="number"
                    bind:value={$pyServerPORT}
                    label="serverPORT"
                    browseBtn={false}
                    lock={true}
                />
                <CustomSwitch bind:selected={$serverDebug} label="serverDebug" />
                <button
                    class="button is-link"
                    class:is-loading={serverCurrentStatus.value.includes('starting')}
                    on:click={window.startServer}
                    disabled={$pyServerReady && serverCurrentStatus.value.includes('running')}
                >
                    STARTserver
                </button>

                {#if $pyServerReady && serverCurrentStatus.value.includes('running')}
                    <button class="button is-danger" on:click={window.stopServer}> STOPserver </button>
                {/if}

                <button class="button is-warning" on:click={updateTCPInfo}>Check TCP</button>
            </div>

            <div class="align">
                <button id="fetchServerROOT" class="button is-link" on:click={updateServerInfo}>fetchServerROOT</button>
                <button
                    class="button is-danger"
                    on:click={() => {
                        serverInfo = []
                    }}>Clear</button
                >
            </div>
        </div>

        <div id="serverInfo__div" class="align box">
            {#each serverInfo as info (info)}
                <span class="has-text-{info.type}" style="width: 100%;">>> {info.value}</span>
            {/each}
        </div>
    </div>
</div>

<style>
    #serverInfo__div {
        display: flex;
        align-content: flex-start;
        overflow: auto;
        user-select: text;
        white-space: pre-wrap;
        align-items: baseline;
        height: calc(42vh - 5rem);
        max-height: calc(42vh - 5rem);
    }
</style>
