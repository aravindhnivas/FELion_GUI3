<script lang="ts">
    import Textfield from '@smui/textfield';
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import computePy_func from '$src/Pages/general/computePy'
    import { createEventDispatcher, tick } from 'svelte';
    import { cloneDeep } from 'lodash-es';

    // let args = {};
    
    const set_config = (config) => {
        ;({trap_temperature, background_pressure, added_pressure, calibration_factor, srgMode, tube_diameter} = config)
        ;([rt, rt_std_dev] = config["room_temperature"])
        const {A, B, C} = config.TakaishiSensuiConstants

        TakaishiSensuiConstants.A.value = A
        TakaishiSensuiConstants.B.value = B
        TakaishiSensuiConstants.C.value = C
    }

    export const set_minimal_config = (config) => {
        trap_temperature[0] = config.temp
        background_pressure[0] = config.pbefore
        added_pressure[0] = config.pafter
        calibration_factor[0] = config.C_factor
        srgMode = config.srgMode
    }
    
    export const updateCurrentConfig = async (config) => {
        if(!config || Object.keys(config).length === 0) return
        set_config(config)
        return await computeNumberDensity(null, true)
    }

    let includeTranspiration = true

    interface DataFromPython {
        F: string
        X: string
        nHe: string
        nHe_transpiration: string
    }
    // let datafromPython: DataFromPython
    let rt = <number>window.db.get('RT') || 300
    let trap_temperature = [4, 0.3]
    let background_pressure = ["1e-8", 0]
    let added_pressure = ["5e-6", 10]
    
    let TakaishiSensuiConstants = {
        A: {value: [6.11, 0], unit: "(K / mm.Pa)^2"},
        B: {value: [4.26, 0], unit: "K / mm.Pa"},
        C: {value: [0.52, 0], unit: "(K / mm.Pa)^0.5"}
    }
    let tube_diameter = [3, 0.1]
    let srgMode = false;
    let calibration_factor = [<number>window.db.get('calibration_factor') ?? 200, 10]
    let rt_std_dev = 1
    $: window.db.set('calibration_factor', Number(calibration_factor[0]))
    
    let numberDensity = null
    let [X, F] = [null, null];

    export const computeNumberDensity = async (e?: Event, get_data=false) => {
        // datafromPython = null
        // args = null
        numberDensity = null
        const room_temperature = [rt, rt_std_dev]
        
        if(Number(trap_temperature[0]) <= 0) return window.createToast("Invalid temperature", "danger")
        
        const changeInPressure = Number(added_pressure[0]) - Number(background_pressure[0])
        if(changeInPressure < 0) return window.createToast("Negative pressure! correct background pressure!!", "danger")
        if(!changeInPressure) return window.createToast("Invalid pressures", "danger")
        const TkConstants = {
            A: TakaishiSensuiConstants.A.value.map(Number),
            B: TakaishiSensuiConstants.B.value.map(Number),
            C: TakaishiSensuiConstants.C.value.map(Number),
        }
        await tick()
        
        const args = {
            srgMode,
            tube_diameter, 
            added_pressure,
            room_temperature,
            trap_temperature,
            background_pressure,
            TakaishiSensuiConstants: TkConstants,
            calibration_factor,
        }

        const datafromPython: DataFromPython = await computePy_func(
            {e, pyfile: 'numberDensity', args}
        )
        
        if(!datafromPython) return Promise.reject('Computation failed')

        numberDensity = {nHe: datafromPython.nHe, nHe_transpiration: datafromPython.nHe_transpiration}
        ;({X, F} = datafromPython)
        if(get_data) return Promise.resolve(cloneDeep({...args, ...datafromPython }))
        return Promise.resolve(dispatch_current_numberdensity(cloneDeep({...args, ...datafromPython })))
    }


    const dispatch = createEventDispatcher();
    const dispatch_current_numberdensity = (datas=null) => {
        const {nHe, nHe_transpiration} = numberDensity
        dispatch('getValue', {nHe: includeTranspiration ? nHe_transpiration : nHe })
        if(datas) dispatch('fullargs', {datas})
    }

</script>

<div class="align h-center">

    <slot name="header" />
    
    <CustomSwitch on:change={async ({detail: {selected}})=>{
        calibration_factor = selected ? [1, 0] : [200, 10]
        return await computeNumberDensity()
    }}
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

<div class="align scroll mt-2 pb-5" on:keypress="{async (e)=>{
    if(e.key==="Enter") {
        await computeNumberDensity()
    }
}}">

    <div style="display: flex; flex-direction: column; padding: 0 1em;">
        
        <div class="align h-center">

            <div class="border__div">
                <Textfield
                    bind:value={trap_temperature[0]}
                    label={'trap_temperature [K]'}
                />
                <Textfield
                    bind:value={trap_temperature[1]}
                    label="std. dev."
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
        
        <div class="align h-center">

            <div class="border__div">
                <Textfield disabled={srgMode}
                    bind:value={calibration_factor[0]}
                    label="Calibration Factor"
                />

                <Textfield disabled={srgMode}
                    bind:value={calibration_factor[1]}
                    label="std.dev."
                />
            </div>

            <div class="border__div">

                <Textfield
                    bind:value={rt}
                    label="Room temperature (K)"
                />

                <Textfield
                    bind:value={rt_std_dev}
                    label="std.dev."
                />
            </div>
        </div>
        <div class="align h-center constants">
            <h2 class="m-0 mt-5" style:width='100%' >Modified Takaishi-Sensui constants (for He gas at 4.3 K)</h2>
            <div>(Reference: J. Chem. Phys. 113, 1738 (2000); https://doi.org/10.1063/1.481976)</div>
            <br>
            
            <div class="border__div">
                {#each Object.keys(TakaishiSensuiConstants) as key (key)}
                    
                <div class="border__div">

                    <Textfield
                        bind:value={TakaishiSensuiConstants[key].value[0]}
                        label={`${key} [${TakaishiSensuiConstants[key].unit}]`}
                        />
                    <Textfield
                        bind:value={TakaishiSensuiConstants[key].value[1]}
                        label="std. dev."
                        />
                </div>
                {/each}
            </div>

            <div class="border__div">
                <Textfield
                    input$min="0"
                    input$step="0.1"
                    type="number"
                    bind:value={tube_diameter[0]}
                    label="connecting tube diameter [mm]"
                />
                <Textfield
                    bind:value={tube_diameter[1]}
                    label="std. dev."
                />
            </div>

            <div class="border__div">
                <Textfield
                    disabled
                    value={X || ''}
                    label="X [mm.Pa / K]"
                />
                <Textfield
                    disabled
                    value={F || ''}
                    label="F (Degree of thermal transpiration)"
                />
            </div>
        </div>
    </div>

</div>
<style>
    .scroll {
        overflow-y: auto; height: 100%;
    }
    .border__div {
        gap: 1em;
        display: flex;

        justify-content: center;
        border: solid 1px white;
        border-radius: 1em;
        padding: 1em;
        flex-wrap: wrap;
    }
</style>
