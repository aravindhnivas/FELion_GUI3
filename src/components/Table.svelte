<script>


    import { fade } from 'svelte/transition'
    import {Icon} from '@smui/icon-button'
    export let head, rows, keys, tableid="", label="table";
    let id = tableid || window.getID()

    const sortTable = (type) => {
        rows = _.orderBy(rows, [type], ["asc"])
    }
</script>

<style>

    * :global(th i) {color: black;}

    .tableIcon {
        display: flex;
        justify-content: center;
        align-items: center;
        color: black;
    }
    
</style>

 <div class="mdc-data-table tableContainer" transition:fade>

    <table class="mdc-data-table__table" aria-label={label} {id}>

        <thead>
            <tr class="mdc-data-table__header-row">
                <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col">#</th>

                {#each head as item, index}
                    <th style="cursor: pointer;" class="mdc-data-table__header-cell mdc-data-table__header-cell--numeric" role="columnheader" scope="col" >
                        <div class="tableIcon" on:click="{(e)=>sortTable(keys[index])}">
                            <Icon class="material-icons" >arrow_downward</Icon>
                            {item}
                        </div>
                    </th>
                {/each}
                
                
            </tr>

        </thead>
        <tbody class="mdc-data-table__content">
            
            {#each rows as row, index (row.id)}
                <tr class="mdc-data-table__row" style="background-color: #fafafa;"> 
                    <td class="mdc-data-table__cell" style="width: 2em;" >{index}</td>

                    {#each keys as key}
                        <td class="mdc-data-table__cell mdc-data-table__cell--numeric" contenteditable="true" bind:innerHTML={row[key]}>{row[key]}</td>
                    {/each}
                </tr>
            {/each}
            
        </tbody>
    </table>

</div>