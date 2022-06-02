<script>
    import { showConfirm } from '$src/components/alert/store'
    import Textfield from '@smui/textfield'
    import HelperText from '@smui/textfield/helper-text'
    import Checkbox from '@smui/checkbox'
    import FormField from '@smui/form-field'
    import { browse } from '../components/Layout.svelte'

    const writePowfile = async () => {
        const contents = `${initContent.trim()}\n${powerfileContent}`.trim()

        const [, error] = await window.fs.writeFile(powfile, contents, 'utf8')
        if (error) {
            return window.createToast("Power file couldn't be saved.", 'danger')
        }
        window.createToast('Power file saved', 'success')
        console.log('powerfile writted: ', powfile)
    }

    function savefile() {
        if (location.length == 0) {
            return openFolder({ save: true })
        }
        if (!window.fs.existsSync(powfile)) return writePowfile()
        return showConfirm.push({
            title: 'Overwrite powerfile?',
            content: 'Do you want to overwrite the powerfile?',
            callback: (response) => {
                console.log(response)
                if (response?.toLowerCase() === 'cancel') return
                writePowfile()
            },
        })
    }

    async function openFolder({ save = false } = {}) {
        const result = await browse()
        if (!result) return
        location = result
        window.db.set('powerfile_location', location)
        window.createToast('Location updated', 'success')
        if (save) savefile()
    }

    let felixHz = 10
    let convert = null
    let felixShots = 16
    let powerfileContent = ''

    let location = window.db.get('powerfile_location') || ''
    let today = new Date()

    const dd = String(today.getDate()).padStart(2, '0')
    const mm = String(today.getMonth() + 1).padStart(2, '0')
    const yy = today.getFullYear().toString().substr(2)

    let filename = `${dd}_${mm}_${yy}-#`

    $: powfile = window.path.resolve(location, `${filename}.pow`)
    $: conversion = '_no_'
    $: convert ? (conversion = '_') : (conversion = '_no_')
    $: initContent =
        `#POWER file\n` +
        `# ${felixHz} Hz FELIX\n` +
        `#SHOTS=${felixShots}\n` +
        `#INTERP=linear\n` +
        `#    IN${conversion}UM (if one deletes the no the firs number will be in \mu m\n` +
        `# wavelength/cm-1      energy/pulse/mJ\n`

    const id = 'Powerfile'
    let display = window.db.get('active_tab') === id ? 'block' : 'none'
</script>

<section
    class="section animate__animated animate__fadeIn"
    {id}
    style="display:{display}"
>
    <div class="box main__container" id="powfileContainer">
        <div class="location__bar">
            <button class="button is-link" on:click={openFolder}>Browse</button>

            <Textfield
                bind:value={location}
                label="Current Location"
                style="flex-grow:1;"
            />
        </div>

        <div class="grid_column__container file__details__bar">
            <Textfield bind:value={filename} label="Filename" />

            <Textfield
                bind:value={felixShots}
                label="FELIX Shots"
                on:change={() => {
                    console.log(felixShots)
                }}
            />

            <Textfield bind:value={felixHz} label="FELIX Hz" />

            <FormField>
                <Checkbox
                    bind:checked={convert}
                    indeterminate={convert === null}
                />

                <span slot="label">Convert to &micro;m</span>
            </FormField>
        </div>

        <div class="power_value__container">
            <Textfield
                textarea
                bind:value={powerfileContent}
                label="Powerfile contents"
                input$aria-controls="powercontent_help"
                input$aria-describedby="powercontent_help"
                style="overflow: hidden; padding: 1em;"
                outline$style="padding: 1em;"
            >
                <HelperText id="powercontent_help" slot="helper">
                    Enter powerfile measured for {filename}.felix file
                    (wavenumber power-in mJ)
                </HelperText>
            </Textfield>

            <button
                class="button is-link"
                style="width: 12em; margin: auto;"
                on:click={savefile}>Save</button
            >
        </div>
    </div>
</section>

<style>
    .section {
        overflow-y: auto;
        height: calc(100vh - 6rem);
        padding: 1em;
    }

    .main__container {
        display: grid;
        height: 100%;
        grid-row-gap: 1em;
        margin: auto;
        width: 100%;
        grid-template-rows: auto auto 1fr;
    }
    .grid_column__container {
        display: grid;
        grid-auto-flow: column;
        grid-column-gap: 1em;
    }

    .location__bar {
        display: flex;
        align-items: baseline;
        gap: 1em;
    }

    .file__details__bar {
        grid-template-columns: repeat(4, 1fr);
    }

    .power_value__container {
        /* padding: 1em; */
        display: grid;
        height: 100%;
        grid-template-rows: 1fr auto auto;
        overflow: hidden;
    }
</style>
