<script lang="ts">
    import { running_processes } from '$src/sveltewritables'
    import { h } from 'gridjs'
    import Grid from 'gridjs-svelte'

    $: process_data = $running_processes.filter(({ pid, pyfile }) => [pid, pyfile, null])
    const columns = [
        {
            name: 'PID',
        },
        'pyfile',
        {
            name: 'close',
            formatter: (cell, row) => {
                return h(
                    'button',
                    {
                        // className: 'button is-danger bg-red',
                        className: cell?.className,
                        onClick: cell?.cb,
                    },
                    'close'
                )
            },
        },
    ]
</script>

<Grid data={process_data} {columns} />
