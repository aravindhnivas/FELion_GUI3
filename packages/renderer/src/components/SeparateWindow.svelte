<script>
    import { tick, onDestroy } from 'svelte'
    import WinBox from 'winbox/src/js/winbox.js'
    import { relayout } from 'plotly.js/dist/plotly-basic'

    export let id = window.getID()
    export let title = 'Title'
    export let active = false
    export let top = 50
    export let bottom = 50

    export let width = '70%'
    export let height = '70%'
    export let x = 'center'
    export let y = 'center'
    export let background = '#634e96'
    export let graphWindow = null
    export let windowReady = false
    export let maximize = true

    async function openGraph() {
        await tick()
        graphWindow = new WinBox({
            root: document.getElementById('pageContainer'),
            mount: document.getElementById(id),
            title,
            x,
            y,
            width,
            height,
            top,
            bottom,
            background,
            onclose: function () {
                active = false
                windowReady = false
                return false
            },
            onfocus: function () {
                windowReady = true
            },
            onresize: function () {
                changeGraphDivWidth()
            },
        })
        graphWindow.maximize(maximize)
    }
    $: if (active) openGraph()

    const changeGraphDivWidth = async (ms = 0) => {
        await tick()
        if (ms > 0) await sleep(ms)
        graphDivs.forEach((id) => {
            if (id.data) {
                relayout(id, { width: id.clientWidth })
            }
        })
    }

    let graphDivs = []
    function lookForGraph() {
        try {
            graphDivs = Array.from(document.querySelectorAll(`#${id} .graph__div`))
        } catch (error) {
            console.log('No graph in this window')
        }
    }

    onDestroy(() => {
        try {
            if (active && graphWindow) {
                console.warn('Window closed')
                graphWindow.close()
            }
        } catch (error) {
            console.warn("Couldn't close the window", error)
        }
    })
</script>

<div {id} class="main_content__div" class:hide={!active}>
    <div class="header_content"><slot name="header_content__slot" /></div>
    <div class="main_content" use:lookForGraph>
        <slot name="main_content__slot" />
    </div>
    <div class="footer_content">
        <div class="left align"><slot name="left_footer_content__slot" /></div>
        <div class="right align"><slot name="footer_content__slot" /></div>
    </div>
</div>

<style lang="scss">
    .main_content__div {
        display: grid;
        max-height: 100%;
        grid-template-rows: auto 1fr auto;
        height: 100%;
        gap: 1em;
        padding: 0;

        .header_content {
            display: grid;
            grid-row-gap: 1em;
            padding: 1em;
        }

        .main_content {
            overflow: auto;
            padding: 0 1em 1em 1em;
        }

        .footer_content {
            display: flex;
            gap: 1em;
            justify-content: flex-end;
            align-items: center;

            border-top: solid 1px;
            padding: 0.5rem;
            background-color: #8965c982;
            .right {
                justify-content: flex-end;
                flex-wrap: nowrap;
            }
        }
    }
</style>
