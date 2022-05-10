<script>
    export let options = []
    export let label = ''
    export let value = ''
    export let multiple = false
    export let update = null
    export let auto_init = false

    $: if (!value && auto_init && options.length > 0) {
        value = options[0]
    }
</script>

<div class:main_container={update}>
    <div class="select" class:is-multiple={multiple}>
        {#if multiple}
            <select
                multiple
                bind:value
                {label}
                size={options.length}
                on:change
                on:click
            >
                {#each options as option}
                    <option value={option}>{option}</option>
                {/each}
            </select>
        {:else}
            <select bind:value {label} on:change on:click>
                <optgroup {label}>
                    {#each options as option}
                        <option value={option}>{option}</option>
                    {/each}
                </optgroup>
            </select>
        {/if}
    </div>

    {#if update}
        <i
            class="material-icons animated faster"
            on:animationend={(event) =>
                event?.target?.classList.remove('rotateIn')}
            on:click={(event) => {
                event?.target?.classList.add('rotateIn')
                update()
            }}
        >
            refresh
        </i>
    {/if}
</div>

<style lang="scss">
    .main_container {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
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
