<script lang="ts">
    import { plotDygraph } from './dygraph_plot'
    import { onMount } from 'svelte'
    export let id = window.getID()

    const data1 = [
        [0, 1, null],
        [1, 2, null],
        [2, 3, 5],
        [3, 0, 2],
        [4, 5, 1],
    ]

    let graph
    onMount(() => {
        graph = plotDygraph(id, data1)
        return () => {
            graph.destroy()
            console.log('graph destroyed')
        }
    })
    let graphContainerWidth: number
    $: graph?.resize(graphContainerWidth - 200, 400)
    // $: console.log(graph)
</script>

<div class="graph__div dygraph_graph__container" bind:clientWidth={graphContainerWidth}>
    <div {id} class="dygraph_graph__div" />
    <div id="{id}-legend" class="dygraph_legend__div" />
</div>

<style>
    .dygraph_graph__container {
        display: grid;
        grid-template-columns: 4fr 1fr;
        background-color: white;
    }

    .dygraph_legend__div {
        padding: 1em;
    }
</style>
