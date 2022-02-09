<script>
    export let options = []
    export let label=""
    export let picked=""
</script>

<div class="select" >

    <select bind:value={picked} {label} on:change >
        <optgroup {label} >
            {#each options as option}
                <option value={option}>{option}</option>
    
            {/each}
        </optgroup>
</select>

</div>

<style lang="scss">
    .select {
        align-self: auto;
        select {
            min-width: 12em;
            &:active, &:hover, &:focus {border-color: white;}
            &::after {border-color: rgb(104, 86, 86);}
        }
        optgroup {
            color: black;
            font-size: medium;
        }
    }
</style>
