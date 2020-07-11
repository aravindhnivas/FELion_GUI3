
<script>
    import Modal1 from '../../../components/Modal1.svelte';
    import CustomCheckList from '../../../components/CustomCheckList.svelte';
    import Textfield from '@smui/textfield';
    import CustomCheckbox from '../../../components/CustomCheckbox.svelte';
    

    import { createEventDispatcher } from 'svelte';
    
    export let active=false, felixFigureWidgets = {};
    const dispatch = createEventDispatcher();

</script>

<style>

    .felix_tkplot_filelist_header {
        border: solid 1px white;
        width: 10em;
        padding: 0.2em;
        display: flex;
        justify-content: center;
        border-radius: 20px;
        margin: auto;
    }

    .felix_tkplot_filelist_div {
        margin-bottom:1em;
    }

    .felix_plotting_div {
        border: solid 1px white;
        border-radius: 20px;
        padding: 1em;
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        margin: 1em 0;
    }

</style>


{#if active}

    <Modal1 bind:active title="FELIX PLOTTING" style="width:70vw;">

        <div slot="content" style="height:40vh;" >
            <div style="display:flex; flex-wrap:wrap;">
                {#each felixFigureWidgets.checkBoxes as {label, options, selected, style, id}(id)}
                    <div style="flex-grow:1; {style}" class="felix_tkplot_filelist_div">
                        <div class="subtitle felix_tkplot_filelist_header">{label}</div>
                        <CustomCheckList style="background: #836ac05c; border-radius: 20px; margin:1em 0;" bind:fileChecked={selected} bind:items={options} height="160px"/>
                    </div>
                {/each}
            </div>
        
            <div class="felix_plotting_div">
                {#each felixFigureWidgets.text as {label, value, id}(id)}
                    <Textfield style="width:12em; margin-bottom:1em;" variant="outlined" type="text" bind:value {label}/>
                {/each}
            </div>

            <div class="felix_plotting_div">
                {#each felixFigureWidgets.number as {label, value, step, id}(id)}
                    <Textfield style="width:12em; margin-bottom:1em;" type="number" {step} bind:value {label}/>
                {/each}
            </div>

            <div class="felix_plotting_div">
                {#each felixFigureWidgets.boolean as {label, value, id}(id)}
                    <CustomCheckbox style="width:12em; margin-bottom:1em;" bind:selected={value} {label} />
                {/each}
            </div>
        </div>

        <button slot="footerbtn" class="button is-link" on:click={()=>{dispatch('submit')}} >Submit</button>
    </Modal1>
    
{/if}