<script lang="ts">
    import { currentTab } from '../svelteWritables'
    import { updateInterval } from '$src/sveltewritables'
    import { activateChangelog } from '$src/js/functions'
    import { onMount, onDestroy } from 'svelte'
    import type { Unsubscribe } from 'conf/dist/source/types'

    let updateError = <string>window.db.get('updateError') || ''
    let updateIntervalCycle: NodeJS.Timer | null = null
    let updating = false

    let unsubscribers: Unsubscribe[] = []

    unsubscribers[0] = window.db.onDidChange('updateError', (err) => {
        updateError = <string>err
    })

    unsubscribers[1] = window.db.onDidChange('delayupdate', (delay) => {
        if (<number>delay) {
            if (updateIntervalCycle) {
                clearInterval(updateIntervalCycle)
            }

            setTimeout(() => {
                updateCheck()
                updateIntervalCycle = setInterval(updateCheck, $updateInterval * 60 * 1000)
            }, 60 * 60 * 1000)
        }
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
                break

            case 'update-downloaded':
                updating = false
                break

            default:
                break
        }
    })

    function updateCheck(event?: ButtonClickEvent): void {
        if (!window.isPackaged) return console.warn('Cannot update un-packed version')
        if (navigator.onLine) return window.checkupdate()
        if (event) return window.createToast('No Internet Connection!', 'warning')
    }

    onMount(async () => {
        // updateCheck()
        if (!window.isPackaged) return
        updateIntervalCycle = setInterval(updateCheck, $updateInterval * 60 * 1000)
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
        App Version {window.appVersion}
    </div>
    <div class="align">
        <div class="align">
            <button class="button is-link" class:is-loading={updating} id="updateCheckBtn" on:click={updateCheck}
                >Check update</button
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

    .errorbox {
        white-space: pre-line;
        height: 100%;
        width: fit-content;
        font-size: medium;
        margin-left: auto;
        border: solid 1px;
    }
</style>
