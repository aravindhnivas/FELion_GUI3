<script>
    export let options = []
    export let label = ''
    export let picked = ''
    export let multiple = false
</script>

<div class="select" class:is-multiple={multiple}>
    {#if multiple}
        <select
            multiple
            bind:value={picked}
            {label}
            size={options.length}
            on:change
        >
            {#each options as option}
                <option value={option}>{option}</option>
            {/each}
        </select>
    {:else}
        <select bind:value={picked} {label} on:change>
            <optgroup {label}>
                {#each options as option}
                    <option value={option}>{option}</option>
                {/each}
            </optgroup>
        </select>
    {/if}
</div>

<style lang="scss">
    .select {
        align-self: auto;
        select {
            min-width: 12em;
            &:active,
            &:hover,
            &:focus {
                border-color: white;
            }
            &::after {
                border-color: rgb(104, 86, 86);
            }
        }
        optgroup {
            color: black;
            font-size: medium;
        }
        select[multiple] {
            height: 4em;
            overflow-x: auto;
            overflow-y: auto;
            option {
                color: white;
                &:checked,
                &:focus {
                    background: #5669d3;
                }
            }
        }
    }
</style>
