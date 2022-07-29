<script>
    import { currentTab, pyVersion } from '../svelteWritables'
</script>

<div class="animate__animated animate__fadeIn" class:hide={$currentTab !== 'About'}>
    <h1>About</h1>
    <div class="content">
        <ul style="user-select: text;" class="ml-0">
            <li>FELionGUI: {window.appVersion}</li>
            <li>{$pyVersion}</li>
            <hr />
            {#each Object.keys(window.versions) as key}
                <li>{key}: {window.versions[key]}</li>
            {/each}
        </ul>
    </div>
</div>
