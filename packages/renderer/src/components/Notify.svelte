<script lang="ts">
    export let label: string
    export let type: string = 'info'
    export let style: string = ''
</script>

{#if label}
    <div class="align block mt-5" style="align-items: baseline; {style}">
        <span class="notification is-{type}" style="width: 100%;">
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
