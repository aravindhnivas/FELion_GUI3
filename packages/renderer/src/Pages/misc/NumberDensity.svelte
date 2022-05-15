<script>
    import Textfield from '@smui/textfield';
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import computePy_func from '$src/Pages/general/computePy'

    let rt = window.db.get('RT') || 300
    $: if (rt) {window.db.set('RT', rt)}
    let conditions = {
        trap_temperature: {value: [5, 5], unit: "K"},
        background_pressure: {value: ["1e-8", 0], unit: "mbar"},
        added_pressure: {value: ["5e-6", 5], unit: "mbar"},
    }

    let calibration_factor = window.db.get('calibration_factor') || 200
    $: if (calibration_factor) {
        window.db.set('calibration_factor', calibration_factor)
    }

    let TakasuiSensuiConstants = {A: 6.11, B: 4.26, C: 0.52}
    let includeTranspiration = true
    let tube_diameter = 3
    let calibration_factor_std_dev = 10
    let rt_std_dev = 0.5
    let datafromPython;
    let srgMode = false;

    const computeNumberDensity = async (e) => {
        const {trap_temperature, background_pressure, added_pressure} = conditions
        datafromPython = await computePy_func(
            {e, pyfile: 'numberDensity', args: {
                trap_temperature: trap_temperature.value,
                background_pressure: background_pressure.value,
                added_pressure: added_pressure.value,
                TakasuiSensuiConstants,
                calibration_factor: [calibration_factor, calibration_factor_std_dev],
                room_temperature: [rt, rt_std_dev],
                tube_diameter, srgMode
            }}
        )
    }


</script>

<div class="box">
    <h2>Number Density</h2>
    {#if datafromPython}
        <h2 class="align h-center" style="user-select: text;">{includeTranspiration ? datafromPython["nHe_transpiration"] : datafromPython["nHe"]} cm-3</h2>
    {/if}
    <hr />

    <div class="align h-center">
        <CustomSwitch
            tooltip="Spinning Rotor Gauge"
            bind:selected={srgMode}
            label="SRG"
            />
            
            <CustomSwitch
            tooltip="correct for thermal-transpiration"
            bind:selected={includeTranspiration}
            label="TT"
            />
        
        <button class="button is-link" on:click={computeNumberDensity}>Compute</button>
    </div>

    <div class="align scroll mt-2 pb-5">

        <div style="display: flex; flex-direction: column; padding: 0 1em;">
            
            <div class="align">

                {#each Object.keys(conditions) as key (key)}
                {@const label = `${key} (${conditions[key].unit})`}
                    <div class="border__div">
                        <Textfield
                            bind:value={conditions[key].value[0]}
                            {label}
                        />
                        <Textfield
                            bind:value={conditions[key].value[1]}
                            label="std. dev. (%)"
                        />
                    </div>
                {/each}

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
</div>

<style>

    .box {max-height: calc(100vh - 10rem);}
    .scroll {
        overflow-y: auto;
        height: 80%;
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
