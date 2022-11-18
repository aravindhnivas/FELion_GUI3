<script lang="ts">
    import Tabs from '$src/components/DynamicTabs.svelte'
    const id = 'Test'
</script>

<section {id}>
    <Tabs on:activeTabChange={(e) => console.log(e.detail)} />
    <div class="container p-5">
        <p class="subtitle">This is a test page</p>
    </div>
</section>
