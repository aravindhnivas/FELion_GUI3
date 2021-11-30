<script>
    export let options = [], style="", label="", picked=""
</script>

<div class="select" >
    <select bind:value={picked} {label} on:change >
    {#each options as option}
        <option value={option} selected={picked === option}>{option}</option>
    {/each}
</select>

</div>

<style lang="scss">
    .select {
        align-self: end;
        select {
            min-width: 12em;
        }
    }
</style>