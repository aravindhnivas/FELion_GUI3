<script lang="ts">
    import { currentTab } from '../svelteWritables'
    import { updateInterval } from '$src/sveltewritables'
    import { activateChangelog } from '$src/js/functions'
    import { onMount, onDestroy } from 'svelte'
    import Notify from '$components/Notify.svelte'
    import type { Unsubscribe } from 'conf/dist/source/types'

    const updateError = window.persistentDB('updateError', '')
    let updateIntervalCycle: NodeJS.Timer | null = null
    let updating = false
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

    unsubscribers[3] = window.db.onDidChange('update-status', (status) => {
        switch (<string>status) {
            case 'checking-for-update':
                updating = true
                break

            case 'update-not-available':
                updating = false
                break

            case 'download-error':
                updating = false
                updateError.set('Download error')
                break

            case 'update-downloaded':
                updating = false
                break

            default:
                break
        }
    })

    onMount(async () => {
        if (!window.isPackaged) return
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
                disabled={!window.isPackaged}
                class="button is-link"
                class:is-loading={updating}
                id="updateCheckBtn"
                on:click={window.checkupdate}>Check update</button
            >

            <button
                class="button is-warning"
                on:click={() => {
                    $activateChangelog = true
                }}>What's New</button
            >
        </div>

        {#if window.isPackaged}
            <div id="update-progress-container">
                <label for="file">Download progress:</label>
                <progress id="update-progress" max="100" value="0"> 0%</progress>
            </div>
            <Notify bind:label={$updateError} type="danger" />
        {/if}
    </div>
</div>

<style lang="scss">
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
