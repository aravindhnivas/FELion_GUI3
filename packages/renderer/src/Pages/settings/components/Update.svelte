<script lang="ts">
    import { currentTab } from '../svelteWritables'
    import { updateInterval } from '$src/sveltewritables'
    import { activateChangelog } from '$src/js/functions'
    import { onMount, onDestroy } from 'svelte'
    import Notify from '$components/Notify.svelte'
    import type { Unsubscribe } from 'conf/dist/source/types'

    const updateError = window.persistentDB('updateError', '')
    let updateIntervalCycle: NodeJS.Timer | null = null
    // let updating = false
    let unsubscribers: Unsubscribe[] = []

    unsubscribers[0] = window.db.onDidChange('updateError', (err) => {
        $updateError = <string>err
    })

    unsubscribers[1] = window.db.onDidChange('delayupdate', (delay) => {
        if (!(window.isPackaged && delay && updateIntervalCycle)) return
        clearInterval(updateIntervalCycle)
        setTimeout(() => {
            window.checkupdate()
            updateIntervalCycle = setInterval(window.checkupdate, $updateInterval * 60 * 1000)
        }, 60 * 60 * 1000)
    })

    let updateReadyToInstall = false

    unsubscribers[3] = window.db.onDidChange('update-status', (status) => {
        updateStatus.text = <string>status

        switch (updateStatus.text) {
            case 'checking-for-update':
                break

            case 'update-not-available':
                break

            case 'download-error':
                updateStatus.type = 'danger'
                updateError.set('Download error')
                break

            case 'update-downloaded':
                updateReadyToInstall = true
                updateStatus.type = 'success'
                break

            default:
                break
        }
    })

    unsubscribers[4] = window.db.onDidChange('updateInterval', (interval) => {
        console.log('updateInterval changed', interval)
        $updateInterval = <number>interval
        if (updateIntervalCycle) {
            clearInterval(updateIntervalCycle)
        }
        updateIntervalCycle = setInterval(window.checkupdate, $updateInterval * 60 * 1000)
    })

    let lastUpdateCheck: string = 'Not checked yet'
    const updateStatus = { text: '', type: 'info' }

    onMount(async () => {
        if (!window.isPackaged) return
        window.checkupdate()
        updateIntervalCycle = setInterval(window.checkupdate, $updateInterval * 60 * 1000)
    })

    onDestroy(() => {
        unsubscribers.forEach((unsubscribe) => unsubscribe())
        if (updateIntervalCycle) {
            clearInterval(updateIntervalCycle)
        }
    })
</script>

<div class="align animate__animated animate__fadeIn" class:hide={$currentTab !== 'Update'}>
    <h1>Update</h1>
    <div class="subtitle" style="width: 100%;">
        Current version: {window.appVersion}
    </div>

    <div class="align">
        <div class="align">
            <button
                class="button is-link"
                class:is-warning={updateReadyToInstall}
                class:is-loading={updateStatus.text === 'checking-for-update'}
                disabled={!window.isPackaged}
                id="updateCheckBtn"
                on:click={() => {
                    updateReadyToInstall ? window.quitAndInstall() : window.checkupdate()
                }}
            >
                {updateReadyToInstall ? 'Quit and Install' : 'Check update'}
            </button>

            <button
                class="button is-warning"
                on:click={() => {
                    $activateChangelog = true
                }}>What's New</button
            >
        </div>

        {#if window.isPackaged}
            <div class="updateCheck_status_div">
                <span>Last checked</span>
                <span class="tag is-warning" id="update-check-status">{lastUpdateCheck}</span>
                <span class="tag is-{updateStatus.type}">{updateStatus.text}</span>
            </div>
            <div id="update-progress-container" style="display:none;">
                <label for="update-progress">Download progress:</label>
                <progress id="update-progress" max="100" value="0"> 0%</progress>
            </div>
            <Notify bind:label={$updateError} type="danger" />
        {/if}
    </div>
</div>

<style lang="scss">
    .updateCheck_status_div {
        display: flex;
        gap: 0.2em;
        align-items: flex-end;
        flex-direction: column;
        margin-left: auto;
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
</style>
