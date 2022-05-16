<script>
    import Textfield from '@smui/textfield';
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import { createEventDispatcher } from 'svelte';

    export let currentConfig = {srgMode: false, temp: 4, pbefore: "1e-8", pafter: "5e-6", calibrationFactor: 200};
    let args = {};
    

    let includeTranspiration = true
    let datafromPython = {}

    let rt = window.db.get('RT') || 300
    let trap_temperature = [currentConfig?.temp ?? 4, 0.3]
    let background_pressure = [currentConfig?.pbefore ?? "1e-8", 0]
    let added_pressure = [currentConfig?.pafter ?? "5e-6", 5]
    
    let TakasuiSensuiConstants = {
        A: {value: 6.11, unit: "(K / mm.Pa)^2"},
        B: {value: 4.26, unit: "K / mm.Pa"},
        C: {value: 0.52, unit: "(K / mm.Pa)^0.5"}
    }
    let tube_diameter = 3
    let srgMode = currentConfig?.srgMode ?? false;
    let calibration_factor = currentConfig?.calibrationFactor || window.db.get('calibration_factor') || 200
    let calibration_factor_std_dev = srgMode ? 0 : 10
    let rt_std_dev = 1
    
    $: if (rt) {window.db.set('RT', rt)}
    $: if (calibration_factor) {
        window.db.set('calibration_factor', calibration_factor)
    }
    export const computeNumberDensity = async (e) => {
        const room_temperature = [rt, rt_std_dev]

        console.log(trap_temperature[0])
        if(trap_temperature[0] < 0) return window.createToast("Invalid temperature", "danger")
        
        const changeInPressure = Number(added_pressure[0]) - Number(background_pressure[0])
        if(!changeInPressure) return window.createToast("Invalid pressures", "danger")

        const TkConstants = {
            A: TakasuiSensuiConstants.A.value,
            B: TakasuiSensuiConstants.B.value,
            C: TakasuiSensuiConstants.C.value,
        }
        args = {
            srgMode,
            tube_diameter, 
            added_pressure,
            room_temperature,
            trap_temperature,
            background_pressure,
            TakasuiSensuiConstants: TkConstants,
            calibration_factor: [calibration_factor, calibration_factor_std_dev],
        }

        datafromPython = await computePy_func(
            {e, pyfile: 'numberDensity', args}
        )

        const nHe = dispatch_current_numberdensity()
        return Promise.resolve(nHe)
    }


    export const get_datas = () => {
        console.log({...args, ...datafromPython })
        return {
            ...args, ...datafromPython 
        }
    }
    const dispatch = createEventDispatcher();

    const dispatch_current_numberdensity = () => {
        console.log(datafromPython)
        const nHe = includeTranspiration ? datafromPython['nHe_transpiration'] : datafromPython['nHe']
        dispatch('getValue', {nHe})
        return nHe
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
                    input$step="0.1"
                    type="number"
                    bind:value={trap_temperature[0]}
                    label={'trap_temperature [K]'}
                />
                <Textfield
                    bind:value={trap_temperature[1]}
                    label="std. dev. (absolute)"
                />
            </div>
            <div class="border__div">
                <Textfield
                    bind:value={background_pressure[0]}
                    label={'background_pressure [mbar]'}
                />
                <Textfield
                    bind:value={background_pressure[1]}
                    label="std. dev. (%)"
                />
            </div>
            <div class="border__div">
                <Textfield
                    bind:value={added_pressure[0]}
                    label={'added_pressure [mbar]'}
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
                <Textfield disabled={srgMode}
                    bind:value={calibration_factor}
                    label="Calibration Factor"
                />

                <Textfield disabled={srgMode}
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
            <h2 class="m-0 mt-5" style:width='100%' >Modified Takaishi-Sensui constants (for He gas at 4.3 K)</h2>
            <div>(Reference: J. Chem. Phys. 113, 1738 (2000); https://doi.org/10.1063/1.481976)</div>
            <br>
            
            <div class="border__div">
                {#each Object.keys(TakasuiSensuiConstants) as key (key)}
                    <Textfield
                        bind:value={TakasuiSensuiConstants[key].value}
                        label={`${key} [${TakasuiSensuiConstants[key].unit}]`}
                    />
                {/each}
            </div>

            <div class="border__div">
                <Textfield
                    type="number"
                    bind:value={tube_diameter}
                    label="connecting tube diameter [mm]"
                />
            
            </div>

            <div class="border__div">
                <Textfield
                    disabled
                    value={datafromPython?.X || ''}
                    label="X [mm.Pa / K]"
                />
                <Textfield
                    disabled
                    value={datafromPython?.F || ''}
                    label="F (Degree of thermal transpiration)"
                />
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
