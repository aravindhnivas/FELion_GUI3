
<script>
    import {difference} from "lodash-es"
    export let pyProcesses=[];
    export let btnName="Submit";
    export let stdOutput="";
</script>

<button class="button is-link ld-ext-right" class:running={pyProcesses.length>0} on:click
    on:pyEvent={ ( {detail: {py}} ) => { pyProcesses = [...pyProcesses, py]; stdOutput="" } } 
    on:pyEventClosed={ ( {detail: {py}} ) => { pyProcesses = difference(pyProcesses, [py]) } } 
    on:pyEventData={ ( {detail: {dataReceived}} ) => {stdOutput += dataReceived; console.log(dataReceived)}} >
    
    {btnName}
    <div class="is-warning tag ld" >{pyProcesses.length || ""}</div>
</button>
