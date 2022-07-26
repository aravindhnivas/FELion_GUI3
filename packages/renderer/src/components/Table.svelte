<script>
    import { orderBy } from 'lodash-es'
    import { scale } from 'svelte/transition'
    import { tick } from 'svelte'

    export let head = []
    export let rows = []
    export let keys = []
    export let id = window.getID()
    export let label = 'table'
    export let userSelect = true

    export let style = 'width: 100%;'
    export let sortOption = false
    export let animateRow = true
    export let disableInput = false
    export let closeOption = true
    export let addextraOption = true

    let sortTypeAscending = true

    if (head.length < 1) {
        head = keys
    }
    const sortTable = (type) => {
        if (sortOption) {
            sortTypeAscending = !sortTypeAscending
            rows = orderBy(rows, [type], [sortTypeAscending ? 'asc' : 'desc'])
        }
    }

    $: animate = animateRow ? scale : () => {}

    const emptyRow = {}
    keys.forEach((key) => (emptyRow[key] = ''))

    const addRow = async () => {
        const id = window.getID()
        rows = [...rows, { ...emptyRow, id }]
        await tick()
        const focusTargetID = `${id}-${keys[0]}`
        document.getElementById(focusTargetID).focus()
    }

    // $: rowKeys = keys.map(key=>({key, id: window.getID()}))
    // let keyedRows = rows.map(row=>({...row, id: window.getID()}))
    // console.log({keyedRows})
</script>

<div {style}>
    {#if $$slots.header}
        <slot name="header" />
    {/if}

    {#if addextraOption}
        <i class="material-symbols-outlined" style="float: right; padding: 0.5em;" on:click={addRow}>add</i>
    {/if}

    <div class="mdc-data-table tableContainer">
        <table
            class="mdc-data-table__table"
            aria-label={label}
            {id}
            style="user-select: {userSelect ? 'text' : 'none'} ;"
        >
            <thead>
                <tr class="mdc-data-table__header-row">
                    <th class="mdc-data-table__header-cell" style="width: 2em;" role="columnheader" scope="col">#</th>

                    {#each head as item, index (item)}
                        <th
                            style="cursor: pointer;"
                            class="mdc-data-table__header-cell"
                            role="columnheader"
                            scope="col"
                        >
                            <div class="tableIcon" on:click={() => sortTable(keys[index])}>
                                {#if sortOption}
                                    <i class="material-symbols-outlined"
                                        >{sortTypeAscending ? 'arrow_upward' : 'arrow_downward'}</i
                                    >
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
                        <td class="mdc-data-table__cell" style="width: 2em;">{index}</td>
                        {#each keys as key (key)}
                            <td class="mdc-data-table__cell  mdc-data-table__cell--numeric" id="{row.id}-{key}">
                                <input
                                    type="text"
                                    bind:value={row[key]}
                                    style="color: black; width: 100%;"
                                    disabled={disableInput}
                                />
                            </td>
                        {/each}
                        {#if closeOption}
                            <td class="mdc-data-table__cell" style="background: #f14668; cursor: pointer; width: 2em;">
                                <i
                                    id={row.id}
                                    class="material-symbols-outlined"
                                    on:click={(e) => {
                                        rows = rows.filter((tb) => tb.id != e.target.id)
                                    }}>close</i
                                >
                            </td>
                        {/if}
                    </tr>
                {/each}
            </tbody>
        </table>
    </div>
</div>

<style>
    * :global(th i) {
        color: black;
    }

    .tableIcon {
        display: flex;
        justify-content: center;
        align-items: center;
        color: black;
    }

    td {
        text-align: center !important;
    }
    .tableContainer {
        overflow-x: auto;
        /* max-width: calc(100vw - 27em); */
    }
</style>
