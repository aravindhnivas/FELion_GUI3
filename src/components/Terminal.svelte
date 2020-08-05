
<script>

    import IconButton, {Icon} from '@smui/icon-button';
    import PreModal from "./PreModal.svelte";
    import {tick} from "svelte";

    import Textfield from '@smui/textfield';

    import CustomSwitch from './CustomSwitch.svelte';
    ///////////////////////////////////////////////////////////////////////////////

    const colorSets = {warning: "#ffdd57", danger:"#f14668", info:"#2098d1", normal:"#fafafa", success:"#20f996"}

    export let commandToRun = localStorage["pythonpath"] || "", commandArgsToRun = "-m, pip", commandResults = [{color:colorSets.normal, results:">> "}], teminalFontSize=20;

    export let commandInputDiv = true, runShell = false;
    
    let preModal = {}
    let openShellTerminal = false;

    const srollTerminalDiv = async () => {
        const terminalDiv = document.getElementById("terminal")
        await tick()
        const scrollTo = terminalDiv.scrollHeight - terminalDiv.clientHeight
        terminalDiv.scrollTo({top:scrollTo, behavior: 'smooth'})
    }

    async function terminalShell(){
        runShell = false
        
        await tick()
        
        srollTerminalDiv()
        
        if (!commandToRun) {return window.createToast("No command entered", "warning")}
        commandResults = [...commandResults , {color:colorSets.normal, results:`>> ${commandToRun} ${commandArgsToRun.split(",").join(" ")}`}]
        let ls;

        
        try {

            ls = spawn(commandToRun, commandArgsToRun.split(",").map(arg=>arg.trim()), { detached: true, stdio: 'pipe', shell: openShellTerminal });
        } catch (error) {preModal.modalContent = error;  preModal.open = true}

        ls.stdout.on("data", data => {
            commandResults = [...commandResults, {color:colorSets.info, results:`>> ${data || ""}`}]
            srollTerminalDiv()

        })
        
        ls.stderr.on("data", data => { 
            commandResults = [...commandResults, {color:colorSets.danger, results:`>> ${data || ""}`}]

            srollTerminalDiv()
        })


        ls.on("close", code => {  

            commandResults = [...commandResults, {color: code === 1 ? colorSets.danger :  colorSets.success, results:`>> child process exited with code ${code}`}]
            srollTerminalDiv()

            const outputLog = `${new Date().toLocaleString()}\n\n-----------------------------------------\nRunning terminal commands\n${commandResults.map(cmd=>cmd.results).join("")}\n-----------------------------------------\n`
            
            try { fs.writeFileSync(path.resolve(__dirname, "output.log"), outputLog)} 
            
            catch (error) { window.createToast("Could not save the outputs to file: output.log", "warning")}

        })
    }

    $: if(runShell) terminalShell()

</script>

<style>

    .box { background-color: #6a50ad8a; overflow-y: auto; height: calc(100vh - 12em);}

    #terminal {

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


<PreModal bind:preModal/>


<div class="content contentBox terminalBox" >

    {#if commandInputDiv}

        <div class="commandInput">
            <div class="run" style="display:flex; align-items:center; margin-bottom:1em;">

                <Textfield  bind:value={commandToRun} label="Enter command to run"/>

                <Textfield  bind:value={commandArgsToRun} label="Enter command-arg"/>
            </div>

            <div class="run" style="display:flex; align-items:center; margin-bottom:1em;">
                
                <IconButton class="material-icons" on:click={terminalShell}>play_arrow</IconButton>
                <CustomSwitch style="margin: 0 1em;" bind:selected={openShellTerminal} label="Shell"/>
                <Textfield type="number" step="1" min="0" bind:value={teminalFontSize} variant="outlined" style="width:7em" label="Font Size"/>

                <IconButton class="material-icons is-pulled-right" style="background: #f14668; border-radius: 2em;" on:click="{()=>commandResults=[{color:colorSets.normal, results:`>> cleared`}] }">clear</IconButton>
            </div>
        </div>
    {/if}

    



    <div class="box" id="terminal" style="height: {commandInputDiv ? 75 : 90}%;">

        {#each commandResults as {color, results}}
            <h1 class="subtitle" style="color:{color}; font-size:{teminalFontSize}px; white-space: pre-wrap; ">{results}</h1>

        {/each}

    </div>

</div>