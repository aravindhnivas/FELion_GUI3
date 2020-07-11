<script>
    import Textfield from '@smui/textfield';
    // import CustomIconSwitch from '../../../components/CustomIconSwitch.svelte';
    import CustomSelect from '../../../components/CustomSelect.svelte';
    import CustomRadio from '../../../components/CustomRadio.svelte';
    // import Ripple from '@smui/ripple';
    import { fade } from 'svelte/transition';

    import { createEventDispatcher } from 'svelte';
    
    export let variables, opoMode, plotData;
    const dispatch = createEventDispatcher();

</script>

<div class="align">

    <button class="button is-link" id="create_baseline_btn" on:click="{(e)=>plotData({e:e, filetype:"baseline", tkplot:"plot"})}"> Create Baseline</button>
    <button class="button is-link" id="felix_plotting_btn" on:click="{(e)=>plotData({e:e, filetype:"felix"})}">FELIX Plot</button>
    <Textfield style="width:7em" variant="outlined" type="number" step="0.5" bind:value={variables.felix.delta} label="Delta"/>
    <button class="button is-link" on:click="{()=>variables.felix.plotModal = true}"> Open in Matplotlib</button>
    <!-- <CustomIconSwitch bind:toggler={openShell} icons={["settings_ethernet", "code"]}/> -->
    <button class="button is-link" on:click="{()=>variables.theory.toggleRow = !variables.theory.toggleRow}">Add Theory</button>
    <button class="button is-link" on:click="{()=>{opoMode = !opoMode}}">OPO</button>

</div>

{#if opoMode}
    <div class="content align" transition:fade >
        <div class="align">
            <CustomSelect style="width:7em;" bind:picked={variables.opo.calibFile} label="Calib. file" options={["", ...variables.opo.calibFiles]}/>
            <Textfield style="width:7em; margin:0 0.5em;" bind:value={variables.opo.delta} label="Delta OPO"/>
            <Textfield style="width:9em" bind:value={variables.opo.calibValue} label="Wn-meter calib."/>
            <button class="button is-link" on:click="{()=>{variables.theory.quickBrowser=false;variables.opo.quickBrowser = !variables.opo.quickBrowser; }}"> Browse File</button>
            <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"opofile"})}">Replot</button>
        </div>
    </div>
{/if}

{#if variables.theory.toggleRow}
    <div class="content align" transition:fade>
        <button class="button is-link" on:click="{()=>{variables.opo.quickBrowser=false;variables.theory.quickBrowser = !variables.theory.quickBrowser; }}"> Browse File</button>
        <Textfield type="number" style="width:7em; margin-right:0.5em;" variant="outlined" bind:value={variables.theory.sigma} label="Sigma"/>
        <Textfield type="number" style="width:7em" variant="outlined" bind:value={variables.theory.scale} label="Scale"/>
        <button class="button is-link" on:click="{(e)=>plotData({e:e, filetype:"theory"})}">Replot</button>
    
    </div>
{/if}

<div style="display:flex;">
    <CustomRadio on:change="{()=>dispatch("replot")}" bind:selected={variables.felix.normMethod} options={["Log", "Relative", "IntensityPerPhoton"]}/>
</div>