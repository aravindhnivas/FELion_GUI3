<script>
    // import {mainPreModal} from "$src/svelteWritable";
    import IconButton from '@smui/icon-button'
    import { tick } from 'svelte'
    import Textfield from '@smui/textfield'
    // import { spawn } from "child_process"

    import CustomSwitch from './CustomSwitch.svelte'
    ///////////////////////////////////////////////////////////////////////////////

    const colorSets = {
        warning: '#ffdd57',
        danger: '#f14668',
        info: '#2098d1',
        normal: '#fafafa',
        success: '#20f996',
    }

    export let commandToRun = window.db.get('pythonpath') || '',
        commandArgsToRun = '-m pip',
        commandResults = [{ color: colorSets.normal, results: '>> ' }],
        teminalFontSize = 20

    export let commandInputDiv = true,
        runShell = false,
        id = 'terminal'

    let openShellTerminal = false

    const srollTerminalDiv = async () => {
        const terminalDiv = document.getElementById(id)
        await tick()
        const scrollTo = terminalDiv.scrollHeight - terminalDiv.clientHeight
        terminalDiv.scrollTo({ top: scrollTo, behavior: 'smooth' })
    }

    async function terminalShell() {
        runShell = false

        await tick()

        srollTerminalDiv()

        if (!commandToRun) {
            return window.createToast('No command entered', 'warning')
        }
        commandResults = [
            ...commandResults,
            {
                color: colorSets.normal,
                results: `>> ${commandToRun} ${commandArgsToRun.split(',').join(' ')}`,
            },
        ]
        let ls

        try {
            commandArgsToRun += ` ${packagesName}`
            ls = window.spawn(
                commandToRun,
                commandArgsToRun.split(' ').map((arg) => arg.trim()),
                { detached: true, stdio: 'pipe', shell: openShellTerminal }
            )
        } catch (error) {
            window.handleError(error)
        }

        ls.stdout.on('data', (writeData) => {
            // const writeData = String.fromCharCode.apply(null, data)
            commandResults = [...commandResults, { color: colorSets.info, results: `>> ${writeData || ''}` }]
            srollTerminalDiv()
        })

        ls.stderr.on('data', (errorData) => {
            // const errorData = String.fromCharCode.apply(null, data)
            commandResults = [...commandResults, { color: colorSets.danger, results: `>> ${errorData || ''}` }]

            srollTerminalDiv()
        })

        ls.on('close', (code) => {
            commandResults = [
                ...commandResults,
                {
                    color: code === 1 ? colorSets.danger : colorSets.success,
                    results: `>> child process exited with code ${code}`,
                },
            ]

            srollTerminalDiv()

            const outputLog = `${new Date().toLocaleString()}\n\n-----------------------------------------\nRunning terminal commands\n${commandResults
                .map((cmd) => cmd.results)
                .join('')}\n-----------------------------------------\n`

            const output = window.fs.writeFileSync(
                window.path.resolve(appInfo.temp, 'FELion_GUI3/output.log'),
                outputLog
            )
            if (window.fs.isError(output)) {
                return window.handleError(output)
            }
        })
    }
    $: if (runShell) terminalShell()

    let installPythonPackagesMode = false,
        packagesName = ''

    const installPythonPackages = () => {
        commandToRun = window.db.get('pythonpath')

        commandArgsToRun = '-m pip install'

        installPythonPackagesMode = !installPythonPackagesMode
    }
</script>

<div class="content contentBox terminalBox">
    {#if commandInputDiv}
        <div class="align" style="margin-bottom: 1em;">
            <button class="button is-link" on:click={installPythonPackages}>Python package installation</button>

            <div class="align">
                {#if installPythonPackagesMode}
                    <Textfield bind:value={packagesName} label="Enter packages name(s)" />
                {:else}
                    <Textfield bind:value={commandToRun} label="Enter command to run" />
                    <Textfield bind:value={commandArgsToRun} label="Enter command-arg" />
                {/if}
            </div>

            <div class="align v-center">
                <IconButton class="material-symbols-outlined" on:click={terminalShell}>play_arrow</IconButton>
                <CustomSwitch style="margin: 0 1em;" bind:selected={openShellTerminal} label="Shell" />
                <Textfield
                    type="number"
                    step="1"
                    min="0"
                    bind:value={teminalFontSize}
                    variant="outlined"
                    style="width:7em"
                    label="Font Size"
                />

                <IconButton
                    class="material-symbols-outlined is-pulled-right"
                    style="background: #f14668; border-radius: 2em;"
                    on:click={() => (commandResults = [{ color: colorSets.normal, results: `>> cleared` }])}
                    >clear</IconButton
                >
            </div>
        </div>
    {/if}

    <div class="box terminal" {id} style="height: {commandInputDiv ? 75 : 90}%;">
        {#each commandResults as { color, results }}
            <h1 class="subtitle" style="color:{color}; font-size:{teminalFontSize}px; white-space: pre-wrap; ">
                {results}
            </h1>
        {/each}
    </div>
</div>

<style>
    .box {
        background-color: #6a50ad8a;
        overflow-y: auto;
        height: calc(100vh - 12em);
    }

    .terminal {
        margin-bottom: 1em;
        background-color: #4a4a4ae6;

        user-select: text;
    }

    .contentBox {
        max-height: 70vh;
        overflow: auto;

        padding-bottom: 1em;
        padding: 1em;
        height: calc(100vh - 12em);
    }
</style>
