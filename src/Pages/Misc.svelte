
<script>

    import Textfield from '@smui/textfield';
    import CustomSwitch from '../components/CustomSwitch.svelte';
    import Terminal from '../components/Terminal.svelte';
    import Tab, {Label} from '@smui/tab';
    import TabBar from '@smui/tab-bar';


    // Fundamental constants
    
    $: c = 299792458 // m/s
    $: plank_constant = 6.62607004e-34 // Js
    $: boltzman_constant = 1.380649e-23 // J/K
    
    $: electron_charge = 1.602176565e-19 // C or eV = J

    $: hz = 1e12.toExponential(4);
    $: eV = (plank_constant/electron_charge) * hz;
    $: kelvin = (plank_constant/boltzman_constant) * hz;

    $: cm_1 = hz/(c*1e2);
    $: um = (c/hz)*1e+6;

    $: ghz = hz*1e-9
    $: nm = (c/hz)*1e+9
    $: J = plank_constant * hz
    $: edit_constants = false

    $: edit_numberDensity_constants = false

    // Number density

    $: pq1_before = 1e-8
    $: pq1_after = 1e-5
    $: temperature = 5
    
    $: calibration_factor = 205.54
    $: rt = 300
    $: ndensity_temp = calibration_factor/(boltzman_constant*1e4*rt**0.5) * ((pq1_after - pq1_before) / temperature**0.5)
    

    $: ndensity = ndensity_temp.toExponential(4)
    let active = "Unit Conversion"

    const navItems = ["Unit Conversion", "Terminal"]
</script>

<style>
    .box { background-color: #6a50ad8a; overflow-y: auto; height: calc(100vh - 12em);}

    * :global(.mdc-text-field--disabled .mdc-text-field__input) {color: #dbdbdb;}
    * :global(.mdc-text-field--disabled .mdc-floating-label) {color: #dbdbdb;}

    .unit_converter_column {margin-right: 1em; height: calc(70vh - 4em);}
    .contentBox {

        max-height: 70vh;
        overflow: auto;
        padding-bottom: 1em;
        padding: 1em;
        height: calc(100vh - 12em);
    }


    .unit_conversion_contents {max-height: 75%; overflow: auto;}

    .misc-nav {

        display: flex;
        align-items: center;
        margin: 0.5em 0;
        overflow: hidden;

        height: 4em;
    }

    #Misc {padding: 0 2em; height: 75vh;}


    @media(max-width: 768px) {
        #unit_conversion_table {
            max-height: 65vh;
        }
    }
    

</style>


<section class="animated fadeIn section" id="Misc" style="display:none">

    <div class="misc-nav box animated fadeInDown" id="navbar" >
        <TabBar tabs={navItems} let:tab bind:active>
            <Tab {tab}> <Label>{tab}</Label> </Tab>
        </TabBar>
    </div>

    {#if active=="Unit Conversion"}
        <div class="columns is-multiline contentBox" id="unit_conversion_table">

            <div class="column box is-4 unit_converter_column">

                <div class="title">Energy Conversion</div>

                <hr>

                <div class="unit_conversion_contents">

                    <Textfield style="width:25%; margin-right:0.5em;"  bind:value={hz} label="Hz" />
                
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={ghz} on:change="{()=>hz=(ghz)*1e+9}" label="GHz" />
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={um} on:change="{()=>hz=(c/um)*1e6}" label="Micron" />
                
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={cm_1} on:change="{()=>hz=cm_1*c*1e2}" label="cm-1" />
                
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={kelvin} on:change="{()=>hz=(boltzman_constant/plank_constant)*kelvin}" label="Kelvin" />
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={eV} on:change="{()=>hz=(electron_charge/plank_constant)*eV}" label="eV" />
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={J} on:change="{()=>hz=(J/plank_constant)}" label="Joule" />
                    <Textfield style="width:25%; margin-right:0.5em;" bind:value={nm} on:change="{()=>hz=(c/nm)*1e9}" label="nm" />

                    <hr>

                    <div class="subtitle is-pulled-left">Fundamental constants</div>
                    <CustomSwitch style="margin: 0 1em;" bind:selected={edit_constants} label="Edit"/>
                    <Textfield style="width:90%; margin-right:0.5em;" disabled={!edit_constants} bind:value={c} label="Speed of light in vaccum" />
                    <Textfield style="width:90%; margin-right:0.5em;" disabled={!edit_constants} bind:value={boltzman_constant} label="Boltzman constant" />
                    <Textfield style="width:90%; margin-right:0.5em;" disabled={!edit_constants} bind:value={plank_constant} label="Plank's constant" />
                    <Textfield style="width:90%; margin-right:0.5em;" disabled={!edit_constants} bind:value={electron_charge} label="Electric charge" />
                </div>


            </div>

            <div class="column box is-4 unit_converter_column">
            
                <div class="title">Number Density</div>
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
    {:else}
        <Terminal />
    {/if}
</section>