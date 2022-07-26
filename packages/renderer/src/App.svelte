<script>
    import { SvelteToast } from '@zerodevx/svelte-toast'
    import Navbar from '$components/Navbar.svelte'
    import Footer from '$components/Footer.svelte'
    import PreModal from '$components/PreModal.svelte'
    import ConfirmAlert from '$src/components/alert/ConfirmAlert.svelte'
    import Home from './Pages/Home.svelte'
    import Powerfile from './Pages/Powerfile.svelte'
    import Normline from './Pages/Normline.svelte'
    import Masspec from './Pages/Masspec.svelte'
    import Timescan from './Pages/Timescan.svelte'
    import THz from './Pages/THz.svelte'

    import Kinetics from './Pages/Kinetics.svelte'
    import Misc from './Pages/Misc.svelte'
    import Settings from './Pages/Settings.svelte'
    import Test from './Pages/Test.svelte'

    const navItems = ['Home', 'Normline', 'Masspec', 'Timescan', 'THz', 'Kinetics', 'Powerfile', 'Misc', 'Settings']
    if (import.meta.env.MODE === 'development') {
        navItems.push('Test')
    }
    const toastOpts = { reversed: true, intro: { y: 100 } }
</script>

<PreModal />
<div class="toast_container">
    <SvelteToast options={toastOpts} />
    <div id="leftToaster">
        <SvelteToast target="right" options={{ initial: 0, intro: { y: 100 } }} />
    </div>
    <div id="rightToaster">
        <SvelteToast target="left" options={{ intro: { y: 100 } }} />
    </div>
</div>
<ConfirmAlert />

<div class="layout">
    <Navbar {navItems} />
    <div id="pageContainer" style="overflow: hidden;">
        <Home />
        <Normline />
        <Masspec />
        <Timescan />
        <THz />
        {#if import.meta.env.MODE === 'development'}
            <Test />
        {/if}
        <Kinetics />
        <Powerfile />
        <Misc />
        <Settings />
    </div>
    <Footer />
</div>

<style>
    .layout {
        display: grid;
        height: 100vh;
        grid-template-rows: auto 1fr auto;
    }
</style>
