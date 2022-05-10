<script>
    import Navbar from '$components/Navbar.svelte'
    import Footer from '$components/Footer.svelte'
    import Home from './Pages/Home.svelte'
    import Powerfile from './Pages/Powerfile.svelte'
    import Normline from './Pages/Normline.svelte'
    import Masspec from './Pages/Masspec.svelte'
    import Timescan from './Pages/Timescan.svelte'
    import THz from './Pages/THz.svelte'
    import Settings from './Pages/Settings.svelte'

    import Misc from './Pages/Misc.svelte'
    import Kinetics from './Pages/Kinetics.svelte'
    import PreModal from '$components/PreModal.svelte'
    import ConfirmAlert from '$src/components/ConfirmAlert.svelte'
    import { onMount, tick } from 'svelte'
    import { SvelteToast } from '@zerodevx/svelte-toast'
    let mounted = false

    onMount(async () => {
        const allbuttons = Array.from(document.querySelectorAll('.button'))
        allbuttons.forEach((button) => button.classList.add('hvr-glow'))
        await tick()
        mounted = true
    })
    const navItems = [
        'Home',
        'Normline',
        'Masspec',
        'Timescan',
        'THz',
        'Kinetics',
        'Powerfile',
        'Misc',
        'Settings',
    ]
    const toastOpts = { reversed: true, intro: { y: 100 } }
</script>

<PreModal />
<SvelteToast options={toastOpts} />
<ConfirmAlert />

<Navbar {navItems} />
<Home />

<div
    id="pageContainer"
    style="overflow: hidden;display: {mounted ? 'block' : 'none'}"
>
    <Normline />
    <Masspec />
    <Timescan />
    <THz />
    <Kinetics />
    <Powerfile />
    <Misc />
    <Settings />
</div>
<Footer />

<style global>
    :root {
        --toastContainerTop: auto;
        --toastContainerRight: auto;
        --toastContainerBottom: 3rem;
        --toastContainerLeft: calc(50vw - 8rem);
    }
</style>
