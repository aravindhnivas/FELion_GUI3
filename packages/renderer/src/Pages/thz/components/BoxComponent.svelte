<script>
    export let title = ""
    export let loaded = false
    let hide = true
</script>

<div class="sub_container__div box align">

    <div class="align" >
        {#if loaded}
            <i class="material-icons">done</i>
        {:else}

            <i class="material-icons">sync_problem</i>
        {/if}
        <div class="subtitle">{title}</div>
        <i class="material-icons toggle" on:click="{()=>{hide = !hide}}">keyboard_arrow_down</i>
    </div>

    <div class="content__div align h-center" class:hide>
        {#if $$slots.control}
        <div class="align h-center">
            <slot name="control" ></slot>
        </div>
        {/if}
        <slot />
    </div>

</div>

<style lang="scss">
    .sub_container__div {
        border: solid 1px dimgrey;
        .content__div {
            max-height: 30rem;
            overflow-y: auto;
        }
        .toggle {
            margin-left: auto;
            border: solid 1px;
            border-radius: 8px;
            padding: 2px;

            &:hover {background-color: #8863c9;}
        
        }
    }
</style>