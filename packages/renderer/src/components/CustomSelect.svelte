<script>
    export let options = [], label="", picked=""
    picked ||= label
</script>

<div class="select" >
    <select bind:value={picked} {label} on:change >
        <option >{label}</option>
    {#each options as option}
        <option value={option}>{option}</option>
    {/each}
</select>

</div>

<style lang="scss">
    .select {
        align-self: auto;
        select {
            min-width: 12em;
            &:active, &:hover {border-color: white;}
            &::after {border-color: grey;}
        }
    }
</style>