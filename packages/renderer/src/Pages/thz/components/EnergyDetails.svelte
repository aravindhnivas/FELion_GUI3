<script lang="ts">
    import { energyUnit, numberOfLevels, energyLevels, energyInfos } from '../stores/energy'
    import { excitedFrom, excitedTo } from '../stores/common'
    import CustomPanel from '$src/components/CustomPanel.svelte'
    import CustomSelect from '$src/components/CustomSelect.svelte'
    import IconButton from '$src/components/IconButton.svelte'
    import BrowseTextfield from '$src/components/BrowseTextfield.svelte'
    import Textfield from '@smui/textfield'
    import WinBox from 'winbox'
    import { wavenumberToMHz, MHzToWavenumber, getYMLFileContents, setID } from '$src/js/utils'
    import BoltzmanDistribution from '../windows/BoltzmanDistribution.svelte'

    export let energyFilename: string = ''

    let openBoltzmanWindow = false
    let boltzmanWindow: WinBox | null = null
    let lock_energylevels = true

    const readFile = async () => {
        console.log(window.path.basename(energyFilename), 'updating energy levels')
        let energyLevelsStore_NoKey: OnlyValueLabel<number>[] = []

        if (energyFilename) {
            ;({ levels: energyLevelsStore_NoKey, unit: $energyUnit } = await getYMLFileContents(energyFilename))
        } else {
            energyLevelsStore_NoKey = []
        }
        const energyLevelsStore: EnergyLevels = energyLevelsStore_NoKey
            .map((e) => ({ ...e, value: Number(e.value) }))
            .map(setID)

        $excitedFrom = energyLevelsStore?.[0].label
        $excitedTo = energyLevelsStore?.[1].label

        $energyInfos[$energyUnit] = energyLevelsStore

        if ($energyUnit === 'cm-1') {
            $energyInfos['MHz'] = energyLevelsStore.map(wavenumberToMHz)
        } else {
            $energyInfos['cm-1'] = energyLevelsStore.map(MHzToWavenumber)
        }
        $numberOfLevels = energyLevelsStore.length
    }

    $: if (window.fs.isFile(energyFilename)) {
        readFile()
    }
</script>

<BoltzmanDistribution bind:active={openBoltzmanWindow} bind:graphWindow={boltzmanWindow} />

<CustomPanel label="Energy Levels" loaded={$energyLevels.length > 0}>
    <BrowseTextfield
        dir={false}
        filetype="yml"
        class="three_col_browse"
        bind:value={energyFilename}
        label="filename"
        lock={true}
    >
        <button class="button is-warning" on:click={readFile}>load</button>
    </BrowseTextfield>

    <div class="align h-center">
        <Textfield
            bind:value={$numberOfLevels}
            input$step={1}
            input$min={0}
            type={'number'}
            label="numberOfLevels (J levels)"
        />
        <CustomSelect options={['MHz', 'cm-1']} bind:value={$energyUnit} label="$energyUnit" />
        <button
            class="button is-link"
            on:click={() => {
                openBoltzmanWindow = true
                setTimeout(() => boltzmanWindow?.focus(), 100)
            }}
        >
            Show Boltzman distribution
        </button>
        <IconButton bind:value={lock_energylevels} icons={{ on: 'lock', off: 'lock_open' }} />
    </div>

    <div class="align h-center">
        {#each $energyLevels as { label, value, id } (id)}
            <Textfield {value} {label} disabled={lock_energylevels} type="number" input$step="0.0001" />
        {/each}
    </div>
</CustomPanel>
