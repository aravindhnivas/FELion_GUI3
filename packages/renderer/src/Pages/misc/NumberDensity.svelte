<script>
    import Textfield from '@smui/textfield';
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import { createEventDispatcher } from 'svelte';

    export let currentConfig = {srgMode: false, temp: 5, pbefore: "1e-8", pafter: "5e-6", calibrationFactor: 200};
    export let args = {};
    

    let includeTranspiration = true
    let datafromPython;

    let rt = window.db.get('RT') || 300
    let trap_temperature = [currentConfig?.temp ?? 4.8, 5]
    let background_pressure = [currentConfig?.pbefore ?? "1e-8", 0]
    let added_pressure = [currentConfig?.pafter ?? "5e-6", 5]
    
    let calibration_factor = currentConfig?.calibrationFactor || window.db.get('calibration_factor') || 200
    let TakasuiSensuiConstants = {A: 6.11, B: 4.26, C: 0.52}
    let tube_diameter = 3
    let calibration_factor_std_dev = 10
    let rt_std_dev = 0.5
    let srgMode = currentConfig?.srgMode ?? false;

    $: if(currentConfig) {
        srgMode = currentConfig?.srgMode ?? srgMode
        trap_temperature[0] = currentConfig?.temp ?? trap_temperature[0]
        background_pressure[0] = currentConfig?.pbefore ?? background_pressure[0]
        added_pressure[0] = currentConfig?.pafter ?? added_pressure[0]
    }

    $: if (rt) {window.db.set('RT', rt)}
    $: if (calibration_factor) {
        window.db.set('calibration_factor', calibration_factor)
    }
    const computeNumberDensity = async (e) => {
        const room_temperature = [rt, rt_std_dev]
        args = {
            srgMode,
            tube_diameter, 
            added_pressure,
            room_temperature,
            trap_temperature,
            background_pressure,
            TakasuiSensuiConstants,
            calibration_factor: [calibration_factor, calibration_factor_std_dev],
        }
        datafromPython = await computePy_func(
            {e, pyfile: 'numberDensity', args}
        )
        dispatch_current_numberdensity()
    }

    const dispatch = createEventDispatcher();
    const dispatch_current_numberdensity = () => {
        const nHe = includeTranspiration ? datafromPython['nHe_transpiration'] : datafromPython['nHe']
        dispatch('getValue', {nHe})
    }
</script>

<div class="align h-center">
    <CustomSwitch
        tooltip="Spinning Rotor Gauge"
        bind:selected={srgMode}
        label="SRG"
        />
        <CustomSwitch on:change={dispatch_current_numberdensity}
        tooltip="correct for thermal-transpiration"
        bind:selected={includeTranspiration}
        label="TT"
        />
    
    <button class="button is-link" on:click={computeNumberDensity}>Compute</button>
</div>

<div class="align scroll mt-2 pb-5">

    <div style="display: flex; flex-direction: column; padding: 0 1em;">
        
        <div class="align">

            <div class="border__div">
                <Textfield
                    bind:value={trap_temperature[0]}
                    label={'trap_temperature (K)'}
                />
                <Textfield
                    bind:value={trap_temperature[1]}
                    label="std. dev. (%)"
                />
            </div>
            <div class="border__div">
                <Textfield
                    bind:value={background_pressure[0]}
                    label={'background_pressure (mbar)'}
                />
                <Textfield
                    bind:value={background_pressure[1]}
                    label="std. dev. (%)"
                />
            </div>
            <div class="border__div">
                <Textfield
                    bind:value={added_pressure[0]}
                    label={'added_pressure (mbar)'}
                />
                <Textfield
                    bind:value={added_pressure[1]}
                    label="std. dev. (%)"
                />
            </div>

        </div>
        
    </div>

    <div style="display: flex; flex-direction: column; padding: 0 1em;">
        
        <div class="align">

            <div class="border__div">
                <Textfield
                    bind:value={calibration_factor}
                    label="Calibration Factor"
                />

                <Textfield
                    bind:value={calibration_factor_std_dev}
                    label="std.dev. (absolute)"
                />
            </div>
            <div class="border__div">

                <Textfield
                    bind:value={rt}
                    label="Room temperature (K)"
                />
                <Textfield
                    bind:value={rt_std_dev}
                    label="std.dev. (absolute)"
                />
            </div>
        </div>
        <div class="align constants">

            <h1 class="subtitle mt-5" style:width='100%' >Takasui-Sensui constants</h1>
            
            <Textfield style="width: 100%;"
                type="number"
                bind:value={tube_diameter}
                label="diameter of the connectingtube (mm)"
            />

            <div class="border__div">
                {#each Object.keys(TakasuiSensuiConstants) as key (key)}
                    <Textfield
                        bind:value={TakasuiSensuiConstants[key]}
                        label={key}
                    />
                {/each}
            </div>

        </div>
    </div>
</div>

<style>
    .scroll {
        overflow-y: auto;
        height: 70%;
    }
    .border__div {
        gap: 1em;
        display: flex;
        justify-content: center;
        width: 100%;
        border: solid 1px white;
        border-radius: 1em;
        padding: 1em;
    }
</style>
