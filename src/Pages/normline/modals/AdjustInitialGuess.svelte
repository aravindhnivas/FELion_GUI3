
<script>
    import {felixPeakTable} from '../functions/svelteWritables';
    import Ripple from '@smui/ripple';
    import { fade } from 'svelte/transition'
    import { createEventDispatcher } from 'svelte';
    import Modal from '../../../components/Modal.svelte';
    import {Icon} from '@smui/icon-button';

    
    export let active=false;
    const dispatch = createEventDispatcher();

    function rearrangePeakTable(e) { $felixPeakTable = _.filter($felixPeakTable, (tb)=>tb.id != e.target.id); }

    $: console.log(`peakTable:`, $felixPeakTable)
    
    const focusFreq = (e) => {e.focus()}

    const sortTable = (type) => { $felixPeakTable = _.orderBy($felixPeakTable, [type], ["asc"]) }

</script>

<style>

</style>

{#if active}

    <Modal bind:active title="Adjust initial guess" >
        <div slot="content" >
                <div class="icon-holder" use:Ripple={[true, {color: 'primary'}]} >
                    <Icon class="material-icons"  on:click="{()=> {$felixPeakTable = [...$felixPeakTable, {freq:0, amp:0, sig:0, id:window.getID()}]}}">add</Icon>
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
                            {#each $felixPeakTable as table, index (table.id)}

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
    </Modal>
    
{/if}