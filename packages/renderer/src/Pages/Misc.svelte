
<script>

    import Textfield from '@smui/textfield';
    import CustomSwitch from '$components/CustomSwitch.svelte';
    import Tab, {Label} from '@smui/tab';
    import TabBar from '@smui/tab-bar';
    import { onDestroy } from 'svelte';

    let fixedDigit = 3

    // Fundamental constants

    $: c = 299792458 // m/s
    $: plank_constant = 6.62607004e-34 // Js
    $: boltzman_constant = 1.380649e-23 // J/K
    $: electron_charge = 1.602176565e-19 // C or eV = J
    $: hz = 1e12.toExponential(fixedDigit);
    $: eV = Number((plank_constant/electron_charge) * hz).toFixed(fixedDigit);
    $: kelvin = Number((plank_constant/boltzman_constant) * hz).toFixed(fixedDigit);
    $: cm_1 = Number(hz/(c*1e2)).toFixed(fixedDigit);
    $: um = Number((c/hz)*1e+6).toFixed(fixedDigit);
    $: ghz = Number(hz*1e-9).toFixed(fixedDigit)
    $: nm = Number((c/hz)*1e+9).toFixed(fixedDigit)
    $: J = Number(plank_constant * hz).toExponential(fixedDigit);
    $: edit_constants = false
    $: edit_numberDensity_constants = false

    // Number density
    $: rt = 300
    $: temperature = 5
    $: pq1_after = 1e-5
    $: pq1_before = 1e-8
    $: calibration_factor = 205.54
    $: ndensity_temp = calibration_factor/(boltzman_constant*1e4*rt**0.5) * ((pq1_after - pq1_before) / temperature**0.5)
    
    $: ndensity = ndensity_temp.toExponential(4)

    let active = db.get("MISC_active_tab") || "Unit Conversion"
    $: if(active) {db.set("MISC_active_tab", active)}
    const navItems = ["Unit Conversion", "Configs", "Terminal"]
    let CONFIGS = db.data()
    const unsubscribe = db.onDidAnyChange((newValue, oldValue)=>{CONFIGS = newValue})
    
    onDestroy(unsubscribe)

</script>


<section class="animated fadeIn section" id="Misc" style="display:none">

    <div class="misc-nav box animated fadeInDown" id="navbar" >

        <TabBar tabs={navItems} let:tab bind:active>
            <Tab {tab}> <Label>{tab}</Label> </Tab>
        </TabBar>
    </div>

    {#if active=="Unit Conversion"}
        <div class="contentBox" id="unit_conversion_table">
            <div class="box">

                <h2>Energy Conversion</h2>
                
                <hr>
                <div class="unit_conversion_contents">

                    <div class="align">
                        <Textfield bind:value={hz} label="Hz" />
                        <Textfield bind:value={ghz} on:change="{()=>hz=(ghz)*1e+9}" label="GHz" />
                        <Textfield bind:value={um} on:change="{()=>hz=(c/um)*1e6}" label="Micron" />
                        <Textfield bind:value={cm_1} on:change="{()=>hz=cm_1*c*1e2}" label="cm-1" />
                        <Textfield bind:value={kelvin} on:change="{()=>hz=(boltzman_constant/plank_constant)*kelvin}" label="Kelvin" />
                        <Textfield bind:value={eV} on:change="{()=>hz=(electron_charge/plank_constant)*eV}" label="eV" />
                        <Textfield bind:value={J} on:change="{()=>hz=(J/plank_constant)}" label="Joule" />
                    
                        <Textfield bind:value={nm} on:change="{()=>hz=(c/nm)*1e9}" label="nm" />
                
                    </div>

                    <hr>
                    <Textfield bind:value={fixedDigit} label="fixedDigit" />
                    <div class="align">
                        <div class="subtitle is-pulled-left">Fundamental constants</div>

                        <CustomSwitch style="margin: 0 1em;" bind:selected={edit_constants} label="Edit"/>
                    </div>
                    <div class="align">
                        <Textfield disabled={!edit_constants} bind:value={c} label="Speed of light in vaccum" />
                        <Textfield disabled={!edit_constants} bind:value={boltzman_constant} label="Boltzman constant" />
                        <Textfield disabled={!edit_constants} bind:value={plank_constant} label="Plank's constant" />
                        <Textfield disabled={!edit_constants} bind:value={electron_charge} label="Electric charge" />
                    </div>

                </div>

            </div>

            <div class="box">
            
                <h2>Number Density</h2>
                <hr>

                <div class="unit_conversion_contents">

                    <div class="subtitle">Main Chamber Press.</div>
                    <Textfield style="width:90%; margin-right:0.5em;" bind:value={pq1_before} label="Before letting in gas" />
                    <Textfield style="width:90%; margin-right:0.5em;" bind:value={pq1_after} label="After letting in gas" />
                    <Textfield style="width:90%; margin-right:0.5em;" bind:value={temperature} label="Temperature" />
                    <Textfield style="width:90%; margin-right:0.5em;" disabled={true} bind:value={ndensity} label="Number density" />
                    <hr>
                    <CustomSwitch style="margin: 0 1em;" bind:selected={edit_numberDensity_constants} label="Edit"/>

                    <Textfield style="width:90%; margin-right:0.5em;" disabled={!edit_numberDensity_constants} bind:value={calibration_factor} label="Calibration Factor" />
                    <Textfield style="width:90%; margin-right:0.5em;" disabled={!edit_numberDensity_constants} bind:value={rt} label="Chamber Temperature (RT)" />

                </div>
            
            </div>
        </div>
    {:else if active=="Configs"}
        <div class="config_main__div box">
            <Textfield style="border: solid 1px #fff7;" value={window.db.path} label="CONFIGS location" disabled />
            <div class="config__div ">
                {#each Object.keys(CONFIGS) as label}
                    <div class="config_content">
                        <Textfield value={CONFIGS[label]} {label} />
                        <button class="button is-warning" on:click="{()=>window.db.delete(label)}">Clear</button>
                    </div>
                {:else}
                    <h1>No data</h1>

                {/each}
            </div>

            <div class="config_footer" style="margin-left: auto;">
                <button class="button is-danger" on:click="{()=>window.db.clear()}">Clear all</button>
            </div>

        </div>

    {/if}
    
</section>

<style lang="scss">
    .contentBox {

        display: flex;
        gap: 1em;
        height: calc(100vh - 14rem);
    }
    .unit_conversion_contents {
        max-height: calc(100vh - 22rem);
        overflow: auto;
    }

    .config_main__div {
        display: grid;
        grid-template-rows: auto 1fr auto;
        max-height: calc(100vh - 15rem);
        gap: 1em;
        .config__div {
            display: grid;
            overflow: auto;
            
            padding-right: 1em;
            gap: 1em;
            .config_content {
                display: grid;
                grid-auto-flow: column;
                grid-template-columns: 1fr auto;
                align-items: baseline;
                gap: 1em;

            }
        }
    }
        
    .misc-nav {
        align-items: center;
        display: flex;
        overflow: hidden;
        height: 4em;
    }

    #Misc { padding: 0 2em; }
    #Misc > div { margin: 1em;}

    @media(max-width: 768px) {
        #unit_conversion_table {max-height: 65vh;}
    }

</style>
