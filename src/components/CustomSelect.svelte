<script>

    import Select, {Option} from '@smui/select'
    export let options = [], style="", label="", picked=""
</script>

<Select bind:value={picked} {label} {style}>

    {#each options as option}
        <Option value={option} selected={picked === option}>{option}</Option>
    {/each}
</Select>