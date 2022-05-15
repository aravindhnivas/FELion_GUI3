<script>
    import { running_processes } from '../svelteWritable'
    import RunningProcess from './RunningProcess.svelte'
    import { SvelteToast, toast } from '@zerodevx/svelte-toast'
    let toastId = null

    const show_process = () => {
        if (toastId) {
            toast.pop(toastId)
            toastId = null
            return
        }

        toastId = toast.push({
            component: {
                src: RunningProcess,
                sendIdTo: 'toastId',
            },
            dismissable: false,
            initial: 0,
            theme: {
                '--toastPadding': '0',
                '--toastMsgPadding': '0',
            },
            target: '_toastFooter',
        })
    }
</script>

<nav
    class="navbar is-fixed-bottom animate__animated animate__fadeInUp"
    id="footer"
>
    <div class="navbar-menu">
        <div class="navbar-start">
            <div class="navbar-item">
                <p>Developed at Dr.Br&uuml;nken's group FELion@FELIX</p>
            </div>
        </div>

        <div class="navbar-end">
            {#if $running_processes.length > 0}
                <div
                    class="navbar-item"
                    on:click={show_process}
                    style="cursor: pointer;"
                >
                    <p>
                        Running {$running_processes.length}
                        {$running_processes.length > 1
                            ? 'processes'
                            : 'process'}
                    </p>
                </div>
            {/if}
            <div class="navbar-item">
                <p>2019-{new Date().getFullYear()} &copy; AN Marimuthu</p>
            </div>
        </div>
    </div>
</nav>

<div id="toastFooter">
    <SvelteToast
        target="_toastFooter"
        options={{ initial: 0, intro: { y: 100 } }}
    />
</div>
