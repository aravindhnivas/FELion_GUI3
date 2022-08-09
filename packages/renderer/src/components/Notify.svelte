<script lang="ts">
    export let label: string
    export let type: string = 'info'
</script>

{#if label}
    <div class="align block mt-5">
        <span class="notification is-{type}">
            {label}
            <button
                class="delete is-danger"
                on:click={() => {
                    label = ''
                }}
            />
        </span>
    </div>
{/if}
