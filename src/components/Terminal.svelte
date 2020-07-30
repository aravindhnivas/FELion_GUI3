
<script>

    import IconButton, {Icon} from '@smui/icon-button';
    import {createToast} from "./Layout.svelte";
    import PreModal from "./PreModal.svelte";
    import {tick} from "svelte";
    import Textfield from '@smui/textfield';

    import CustomSwitch from '../components/CustomSwitch.svelte';

    let colorSets = {warning: "#ffdd57", danger:"#f14668", info:"#2098d1", normal:"#fafafa", success:"#20f996"}

    let commandToRun = "", commandArgsToRun = "", commandResults = [], teminalFontSize=20;

    $: console.log(commandResults)
    
    let preModal = {}

    let openShellTerminal = false;

    async function terminalShell(){
    
        await tick()

        if (!commandToRun) {return createToast("No command entered", "warning")}
        commandResults = [...commandResults , {color:colorSets.normal, results:`>> ${commandToRun} ${commandArgsToRun.replace(",", " ")}`}]
        
        let ls;

        try {

            ls = spawn(commandToRun, commandArgsToRun.split(",").map(arg=>arg.trim()), { detached: true, stdio: 'pipe', shell: openShellTerminal });
        } catch (error) {preModal.modalContent = error;  preModal.open = true}

        ls.stdout.on("data", data => { 

            commandResults = [...commandResults, {color:colorSets.info, results:`>> ${data || ""}`}]
        })

        
        ls.stderr.on("data", data => { 
            commandResults = [...commandResults, {color:colorSets.danger, results:`>> ${data || ""}`}]
        })
        
        ls.on("close", code => {  
            commandResults = [...commandResults, {color: code === 1 ? colorSets.danger :  colorSets.success, results:`>> child process exited with code ${code}`}]
            const outputLog = `${new Date().toLocaleString()}\n\n-----------------------------------------\nRunning terminal commands\n${commandResults.map(cmd=>cmd.results).join("")}\n-----------------------------------------\n`

            try {
                fs.writeFileSync(path.resolve(__dirname, "output.log"), outputLog)
            } catch (error) { createToast("Could not save the outputs to file: output.log", "warning")}

        })

    }
</script>


<style>

    .box { background-color: #6a50ad8a; overflow-y: auto; height: calc(100vh - 12em);}


    #terminal {
        height: 75%;
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

    <div class="box" id="terminal">

        <div>

            <div > 
                {#each commandResults as {color, results}}

                        <h1 class="subtitle" style="color:{color}; font-size:{teminalFontSize}px; white-space: pre-wrap; ">{results}</h1>
                {/each}

            </div>
        </div>
    
    </div>

</div>