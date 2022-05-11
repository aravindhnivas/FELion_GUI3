<script>
    import Editor from '$components/Editor.svelte'
    import { computeKineticCodeScipy } from '../functions/computeKineticCode'
    // import { resizableDiv } from '$src/js/resizableDiv.js'
    export let ratek3
    export let k3Guess
    export let kCIDGuess
    export let ratekCID = ''
    export let location = ''
    export let savefilename = ''
    export let reportRead = false
    export let reportSaved = false
    export let nameOfReactants = ''
    let editor

    // const change = { width: false, height: true }
    // const edges = { bottom: true, top: false, left: false, right: false }
</script>

<div class="report-editor-div" id="kinetics-editor__div">
    <Editor
        filetype="kinetics"
        showReport={true}
        mount="#kinetics-editor__div"
        id="kinetics-editor"
        mainTitle="Kinetic Code"
        bind:savefilename
        {location}
        enable_location_browser={false}
        bind:editor
        bind:reportRead
        bind:reportSaved
    >
        <svelte:fragment slot="btn-row">
            <button
                class="button is-warning"
                on:click={() => {
                    if (!nameOfReactants)
                        return window.createToast('No data available', 'danger')
                    const dataToSet = computeKineticCodeScipy({
                        ratek3,
                        ratekCID,
                        nameOfReactants,
                        k3Guess,
                        kCIDGuess,
                    })
                    if (dataToSet) {
                        reportSaved = false
                        editor?.setData(dataToSet)
                        window.createToast('data comupted')
                    }
                }}>compute</button
            >
        </svelte:fragment>
    </Editor>
</div>
