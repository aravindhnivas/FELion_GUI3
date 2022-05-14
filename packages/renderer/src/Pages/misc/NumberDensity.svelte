<script>
    import Textfield from '@smui/textfield';
    import CustomSwitch from '$components/CustomSwitch.svelte'
    import {boltzmanConstant} from '$src/js/constants';

    let rt = window.db.get('RT') || 300
    $: if (rt) {window.db.set('RT', rt)}
    let conditions = {
        temperature: {value: [5, 5], unit: "K"},
        background_pressure: {value: ["1e-8", 0], unit: "mbar"},
        added_pressure: {value: ["1e-5", 5], unit: "mbar"},
    }

    let calibration_factor = window.db.get('calibration_factor') || 200
    $: if (calibration_factor) {
        window.db.set('calibration_factor', calibration_factor)
    }
    const Kb_in_cm = boltzmanConstant * 1e4
    $: changeInPressure = Number(conditions.added_pressure.value[0]) - Number(conditions.background_pressure.value[0])
    $: CONSTANT = calibration_factor / ( Kb_in_cm * rt ** 0.5)
    $: ndensity = (CONSTANT * changeInPressure) / (conditions.temperature.value[0] ** 0.5)

    let TakasuiSensuiConstants = {A: 6.11, B: 4.26, C: 0.52}
    let includeTranspiration = false
    let srgMode = false
</script>

<div class="box">
    <h2>Number Density</h2>
    <h2 class="flex is-right">{ndensity.toExponential(4)} cm-3</h2>
    <hr />

    <div class="scroll">
        <div style="display: flex; flex-direction: column; padding: 0 1em;">
            
            <div class="align">
                {#each Object.keys(conditions) as key (key)}

                    {@const label = `${key} (${conditions[key].unit})`}
                    <div>
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

            <div class="align">
                <CustomSwitch
                    bind:selected={includeTranspiration}
                    label="transpiration"
                />

                <button class="button is-warning m-5">Compute</button>
            </div>
            
        </div>
        <!-- <hr /> -->
        <div style="display: flex; flex-direction: column; padding: 0 1em;">
            
            <div style="align">
    
                <Textfield
                    bind:value={calibration_factor}
                    label="Calibration Factor"
                />

                <Textfield
                    bind:value={rt}
                    label="Room temperature (K)"
                />

                <div class="align constants">
                    
                    <h1 class="subtitle mt-5" style:width='100%' >Takasui-Sensui constants</h1>
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

<style lang="scss">
    .box {max-height: calc(100vh - 15rem);}
    .scroll {
        overflow-y: auto;
        height: 70%;
    }
</style>