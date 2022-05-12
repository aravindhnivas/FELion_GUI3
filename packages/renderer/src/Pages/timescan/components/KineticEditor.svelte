<script>
    import Editor from '$components/Editor.svelte'
    import { computeKineticCodeScipy } from '../functions/computeKineticCode'

    export let ratek3
    export let k3Guess
    export let kCIDGuess
    export let ratekCID = ''
    export let location = ''
    export let savefilename = ''
    export let reportRead = false
    export let reportSaved = false

    export let nameOfReactants = ''
    export let loss_channels = []

    let editor
    let computedCode

    const computeSliders = () => {
        const computedCode_new = new computeKineticCodeScipy({
            ratek3,
            ratekCID,
            nameOfReactants,
            k3Guess,
            kCIDGuess,
            loss_channels,
        })
        const data = computedCode_new.sliders + computedCode?.model
        update_editor(data)
    }

    const update_editor = (data) => {
        reportSaved = false

        const setData = `# Kinetics code\n${data}\n\n`
        editor?.setData(setData)
        window.createToast('data comupted')
    }
    const compute = () => {
        if (!nameOfReactants) {
            return window.createToast('No data available', 'danger')
        }
        computedCode = new computeKineticCodeScipy({
            ratek3,
            ratekCID,
            nameOfReactants,
            k3Guess,
            kCIDGuess,
            loss_channels,
        })
        update_editor(computedCode.fullEquation)
    }
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
            <div class="align">
                <button class="button is-link" on:click={computeSliders}
                    >update sliders</button
                >
                <button class="button is-link" on:click={compute}
                    >compute full equations</button
                >
            </div>
        </svelte:fragment>
    </Editor>
</div>
