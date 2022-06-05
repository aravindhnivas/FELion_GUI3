<script lang="ts">
    import HelperText from '@smui/textfield/helper-text'
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

<div class="container">
    <span style="font-size: small;">{label}</span>
    <!-- <HelperText>{label}</HelperText> -->
    <div class:contanier-with-icon={update}>
        <div class="select" class:is-multiple={multiple}>
            {#if multiple}
                <select multiple bind:value {label} size={options.length} on:change on:click on:dblclick>
                    {#each options as option}
                        <option value={option}>{option}</option>
                    {/each}
                </select>
            {:else}
                <select bind:value {label} on:change on:click on:dblclick>
                    <!-- <optgroup {label}> -->
                    {#each options as option}
                        <option value={option}>{option}</option>
                    {/each}
                    <!-- </optgroup> -->
                </select>
            {/if}
        </div>

        {#if update}
            <i
                class="material-icons animate__animated animate__faster"
                on:animationend={(event) => event?.target?.classList.remove('animate__rotateIn')}
                on:click={(event) => {
                    event?.target?.classList.add('animate__rotateIn')
                    update()
                }}
            >
                refresh
            </i>
        {/if}
    </div>
</div>

<style lang="scss">
    .container {
        display: flex;
        flex-direction: column;
    }

    .contanier-with-icon {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    .select {
        align-self: auto;
        select {
            min-width: 12em;

            // background: #6249a5;
            &:active,
            &:hover,
            &:focus {
                border-bottom: solid 2px white;
            }
            border: none;
            border-bottom: solid 2px #c5c3c3;

            // option {
            //     color: white;
            // }
        }

        select::-webkit-scrollbar {
            width: 0.5rem;
            height: 8px;
            background-color: white;
        }

        select::-webkit-scrollbar-thumb {
            background-color: #5669d3;
        }
        optgroup {
            // color: black;
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
