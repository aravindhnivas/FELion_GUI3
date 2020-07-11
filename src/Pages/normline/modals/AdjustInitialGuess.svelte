
<script>
    import Ripple from '@smui/ripple';
    import { fade } from 'svelte/transition'
    import { createEventDispatcher } from 'svelte';
    import Modal1 from '../../../components/Modal1.svelte';
    import {Icon} from '@smui/icon-button'
    
    export let modalActivate=false, peakTable = [];
    const dispatch = createEventDispatcher();
    let originalTable;
    function rearrangePeakTable(e) {

        peakTable = _.filter(peakTable, (tb)=>tb.id != e.target.id);
        removedTable = _.differenceBy(originalTable, peakTable)
        console.log(originalTable, peakTable, removedTable)

    }

    $: console.log(peakTable)
    
    const focusFreq = (e) => {e.focus()}

    const sortTable = (type) => {
        peakTable = _.orderBy(peakTable, [type], ["asc"])

        // peakTable = _.reverse(peakTable)
    }

</script>

<style>

</style>


{#if modalActivate}

    <Modal1 bind:active={modalActivate} title="Adjust initial guess" >
        <div slot="content" >
                <div class="icon-holder" use:Ripple={[true, {color: 'primary'}]} >
                    <Icon class="material-icons"  on:click="{(e)=> {peakTable = [...peakTable, {freq:0, amp:0, sig:0, id:window.getID()}]}}">add</Icon>
                </div>

                <!-- Data Table -->

                <div class="mdc-data-table tableContainer" transition:fade>

                    <table class="mdc-data-table__table" aria-label="adjustPeaks">

                        <thead>
                
                            <tr class="mdc-data-table__header-row">
                                <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col"></th>
                                <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" on:click="{()=>sortTable("freq")}">Frequency</th>
                                <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" on:click="{()=>sortTable("amp")}">Amplitude</th>
                                <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" on:click="{()=>sortTable("sig")}">Sigma</th>
                                <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col"></th>
                            </tr>
                        </thead>
                        <tbody class="mdc-data-table__content">
                            {#each peakTable as table, index (table.id)}

                                <tr class="mdc-data-table__row" style="background-color: #fafafa;"> 
                                    <td class="mdc-data-table__cell" style="width: 2em;" >{index}</td>
                                    <td class="mdc-data-table__cell mdc-data-table__cell--numeric"  ><input style="color:black" type="number" step="0.05" bind:value="{table.freq}" use:focusFreq></td>
                                    <td  class="mdc-data-table__cell mdc-data-table__cell--numeric" ><input style="color:black" type="number" step="0.05"  bind:value="{table.amp}"></td>
                                    <td class="mdc-data-table__cell mdc-data-table__cell--numeric" ><input style="color:black" type="number" step="0.5"  bind:value="{table.sig}"></td>
                                    <td class="mdc-data-table__cell" style="background: #f14668; cursor: pointer; width: 2em;" >
                                        <Icon id="{table.id}" class="material-icons" on:click="{(e)=> {rearrangePeakTable(e)}}">close</Icon>
                                    </td>
                                </tr>
                            {/each}
                            
                        </tbody>
                    </table>
                </div>

        </div>
        <button slot="footerbtn" class="button is-link" on:click="{()=>dispatch('save')}" >Save</button>
    </Modal1>
    
{/if}