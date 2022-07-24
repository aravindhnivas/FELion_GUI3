<script lang="ts">
    import Textfield from '@smui/textfield'
    // import { persistentDB } from '$src/js/persistentDB'
    // import { onDestroy } from 'svelte'

    const id = 'Test'

    const db_test_value = window.persistentDB(id, 'test_value')
    // onDestroy(() => {
    //     unsubscribe()
    // })
</script>

<section {id}>
    <div class="align">
        <Textfield bind:value={$db_test_value} label="Test" />
    </div>
</section>
