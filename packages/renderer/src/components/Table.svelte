<script>

    import {orderBy} from "lodash-es"
    import { scale } from 'svelte/transition';
    import {Icon} from '@smui/icon-button';
    import {tick} from "svelte";

    export let head=[]
    export let rows=[]
    export let keys=[]
    export let id=getID()
    export let label="table"
    
    export let userSelect=true
    export let style="width: 100%;";
    export let sortOption = false
    export let closeOption = true
    export let addextraOption = true
    export let animateRow = true;

    const keyIDSets = keys.map(key=>({key, id:getID()}))
    $: console.log({rows, keyIDSets})
    let sortTypeAscending = true;
    const sortTable = (type) => { 
        if(sortOption) {
            sortTypeAscending = !sortTypeAscending
            rows = orderBy(rows, [type], [sortTypeAscending ? "asc" : "desc"])
        }
    }

    $: animate = animateRow ? scale : ()=>{}

    const emptyRow = {}
    keys.forEach(key=>emptyRow[key] = "")

    const addRow = async () => {
        const id = getID()
        rows = [...rows, {...emptyRow, id}]
        await tick()
        const focusTargetID = `${id}-${keys[0]}`
        document.getElementById(focusTargetID).focus()
    }

</script>

<div {style}>
    {#if addextraOption}
        <div class="icon-holder" >
            <Icon class="material-icons"  on:click="{addRow}">add</Icon>
        </div>
    {/if}

    <div class="mdc-data-table tableContainer" >

        <table class="mdc-data-table__table" aria-label={label} {id} style="user-select: {userSelect ? 'text' : 'none'} ;">
            <thead>

                <tr class="mdc-data-table__header-row">

                    <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col">#</th>


                    {#each head as item, index }

                        <th style="cursor: pointer;" class="mdc-data-table__header-cell" role="columnheader" scope="col" >

                            <div class="tableIcon" on:click="{()=>sortTable(keys[index])}">
                                {#if sortOption}
                                    <Icon class="material-icons" >{sortTypeAscending ? "arrow_upward": "arrow_downward"}</Icon>
                                {/if}

                                {item}
                            </div>
                        </th>

                    {/each}
                    
                </tr>
            </thead>

            <tbody class="mdc-data-table__content">
                {#each rows as row, index (row.id)}

                    <tr class="mdc-data-table__row" style="background-color: #fafafa;" transition:animate> 
                    <td class="mdc-data-table__cell" style="width: 2em;" >{index}</td>
                    {#each keys as key (key)}
                        <td class="mdc-data-table__cell  mdc-data-table__cell--numeric" id="{row.id}-{key}">
                            <input type="text" bind:value={row[key]} style="color: black; width: 100%;">
                        </td>
                    {/each}
                    {#if closeOption}
                        <td class="mdc-data-table__cell" style="background: #f14668; cursor: pointer; width: 2em;">
                            <Icon id="{row.id}" class="material-icons" on:click="{(e)=> {rows = rows.filter((tb)=>tb.id != e.target.id)}}">close</Icon>

                        </td>
                    {/if}
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>

<style>

    * :global(th i) {color: black;}
    
    .tableIcon {
        display: flex;
        justify-content: center;
        align-items: center;
        color: black;
    }
    
    td {text-align: center!important;}
    .tableContainer {
        overflow-x: auto;
        /* max-width: calc(100vw - 27em); */
    }
</style>
