<script lang="ts">
    import { running_processes } from '$src/sveltewritables'
    import STable from './STable.svelte'
    import MenuSurface from '@smui/menu-surface'
    import type { MenuSurfaceComponentDev } from '@smui/menu-surface'

    let surface: MenuSurfaceComponentDev
</script>

<div class="animate__animated animate__fadeInUp" id="footer">
    <div class="navbar-menu">
        <div class="navbar-start">
            <div class="navbar-item">
                <p>Developed at Dr.Br&uuml;nken's group FELion@FELIX</p>
            </div>
        </div>

        <div class="navbar-end">
            {#if $running_processes.length > 0}
                <MenuSurface
                    style="background: var(--background-color);"
                    bind:this={surface}
                    anchorCorner="BOTTOM_START"
                    anchorMargin={{ top: 0, right: 50, bottom: 0, left: 0 }}
                >
                    <!-- <ProcessGridTable /> -->
                    <STable idKey="pid" rows={$running_processes} rowKeys={['pid', 'pyfile', 'close']} />
                    <!-- <RunningProcess /> -->
                </MenuSurface>
                <div
                    transition:fade
                    role="presentation"
                    class="navbar-item process__notify_container"
                    on:click={() => surface.setOpen(true)}
                >
                    Running {$running_processes.length}
                    {$running_processes.length > 1 ? 'processes' : 'process'}
                </div>
            {/if}
            <div class="navbar-item">
                <p>2019-2022 &copy; AN Marimuthu</p>
            </div>
        </div>
    </div>
</div>

<style lang="scss">
    .process__notify_container {
        cursor: pointer;
    }
    .navbar-end .navbar-item:not(:only-child) {
        border-left: solid 1px;
    }
</style>
