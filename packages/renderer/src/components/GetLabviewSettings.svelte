<script>
    import Modal from './Modal.svelte'
    import { fade } from 'svelte/transition'
    import { afterUpdate } from 'svelte'
    import Textfield from '@smui/textfield'
    import CustomSelect from './CustomSelect.svelte'

    import CustomSwitch from './CustomSwitch.svelte'
    export let currentLocation, fullfileslist, fileChecked
    export let active = false

    const settingsVariable = {

        b0: ['m03_ao09_bl0', 'm03_ao09_high', 'm03_ao09_width'],
        bq0: 'm03_ao01_bq0',
        bq5: 'm03_ao03_bq5',
        q1float: 'm03_ao15_qd1_float',
        q2float: 'm04_ao09_qd2_float',
        res: 'm03_ao13_reso',
        bqLenses: [
            'm03_ao08_bq1',
            'm03_ao07_bq2',
            'm03_ao06_bq3',
            'm03_ao05_bq4',
        ],
        benderLenses: ['m04_ao01_b_in', 'm04_ao00_b_outer', 'm04_ao02_b_inner'],
        se: [
            'm04_ao03_se_trap_in',
            'm04_ao03_se_delay',
            'm04_ao03_se_high',
            'm04_ao03_se_width',
        ],
        sa: [
            'm04_ao04_sa_trap_out',
            'm04_ao04_sa_delay',
            'm04_ao04_sa_high',
            'm04_ao04_sa_width',
        ],
        trapfloat: 'm04_ao05_trap_float',
        bl4: 'm04_ao07_bl4',
        bl5: 'm04_ao08_bl5',
    }

    const style = 'width:14em; height:3.5em; margin-right:0.5em'
    let fileContents = ''

    let variableValues = {}
    let settingsLoaded = false
    afterUpdate(() => {
        const fullFilename = pathJoin(currentLocation, selected_file)
        console.log(fullFilename)
        settingsLoaded = false

        if (fs.existsSync(fullFilename) && selected_file) {
            fileContents = fs.readFileSync(fullFilename)

            for (const line of fileContents.split('\n')) {
                if (
                    line.trim().length > 0 &&
                    line.startsWith('# Sect01 Ion Source')
                ) {
                    let tempLine = line.split(' ')
                    variableValues[tempLine[7]] = parseFloat(tempLine[9])
                }
            }
            settingsLoaded = true
        }
    })
    let showAllFiles = true

    $: displayFiles = showAllFiles ? fullfileslist : fileChecked

    const labelRowB0 = ['B0 Low', 'B0 high', 'B0 Width']

    const labelRowSE = ['Trap-in', 'SE delay', 'SE high', 'SE Width']
    const labelRowSA = ['Trap-out', 'Trap time (ms)', 'SA high', 'SA Width']

    const bqlensLabel = ['bq1', 'bq2', 'bq3', 'bq4']
    const benderLabel = ['Bender in', 'Bender outer', 'Bender inner']
    let selected_file = ''
</script>

<button
    class="button is-link"
    on:click={() => {
        active = true
    }}>GetLabviewSettings</button
>

{#if active}
    <Modal title="Labview Settings" bind:active>
        <div slot="content" transition:fade>
            <CustomSwitch
                style="margin: 0 1em;"
                bind:selected={showAllFiles}
                label="show all"
            />
            <CustomSelect
                bind:picked={selected_file}
                label="Filename"
                options={displayFiles}
            />

            {#if settingsLoaded}
                <div class="container">
                    <div class="b0 col">
                        {#each settingsVariable.b0 as item, index (item)}
                            <Textfield
                                {style}
                                value={variableValues[item]}
                                label={`${labelRowB0[index]} (${item})`}
                            />
                        {/each}
                    </div>

                    <div class="row">
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.q1float]}
                            label="Quad 1 float ({settingsVariable.q1float})"
                        />
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.bq0]}
                            label="bq0 ({settingsVariable.bq0})"
                        />
                    </div>
                    <div class="bqLenses col">
                        {#each settingsVariable.bqLenses as item, index (item)}
                            <Textfield
                                {style}
                                value={variableValues[item]}
                                label={`${bqlensLabel[index]} (${item})`}
                            />
                        {/each}
                    </div>

                    <div class="row">
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.bq5]}
                            label="bq5 ({settingsVariable.bq5})"
                        />
                    </div>
                    <div class="benderLenses col">
                        {#each settingsVariable.benderLenses as item, index (item)}
                            <Textfield
                                {style}
                                value={variableValues[item]}
                                label={`${benderLabel[index]} (${item})`}
                            />
                        {/each}
                    </div>

                    <div class="row">
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.bl4]}
                            label="bl4 ({settingsVariable.bl4})"
                        />
                    </div>
                    <div class="se row">
                        {#each settingsVariable.se as item, index (item)}
                            <Textfield
                                {style}
                                value={variableValues[item]}
                                label={`${labelRowSE[index]} (${item})`}
                            />
                        {/each}
                    </div>

                    <div class="row">
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.trapfloat]}
                            label="trapfloat ({settingsVariable.trapfloat})"
                        />
                    </div>

                    <div class="sa row">
                        {#each settingsVariable.sa as item, index (item)}
                            <Textfield
                                {style}
                                value={variableValues[item]}
                                label={`${labelRowSA[index]} (${item})`}
                            />
                        {/each}
                    </div>

                    <div class="row" style="padding: 1em 0;">
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.bl5]}
                            label="bl5 ({settingsVariable.bl5})"
                        />
                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.res]}
                            label="Resolution ({settingsVariable.res})"
                        />

                        <Textfield
                            {style}
                            value={variableValues[settingsVariable.q2float]}
                            label="Quad 2 float ({settingsVariable.q2float})"
                        />
                    </div>
                </div>
            {/if}
        </div>
    </Modal>
{/if}

<style>
    .row {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
    }
    .row,
    .col {
        margin-bottom: 2em;
    }
    .col {
        display: grid;
    }
    .container {
        display: grid;
        place-items: center;
        /* margin: 1em 6em; */
        /* overflow-y: auto; */
        /* max-height: 30vh; */
        padding: 1em;
        /* border: solid 1px; */
        /* border-radius: 1em; */
        /* justify-content: center; */
    }
</style>
