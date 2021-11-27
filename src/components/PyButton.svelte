
<script>
    
    export let pyProcesses=[];
    export let btnName="Submit";
    export let showLoading=false;
    export let stdOutput="";

    $: loading =  (showLoading&&pyProcesses.length) ? true : false

</script>


<button class="button is-link ld-ext-right" class:running={pyProcesses.length>0} on:click
    on:pyEvent={ ( {detail: {py}} ) => { pyProcesses = [...pyProcesses, py] } } 
    on:pyEventClosed={ ( {detail: {py}} ) => { pyProcesses = window._.difference(pyProcesses, [py]) } } 
    on:pyEventData={ ( {detail: {dataReceived}} ) => {stdOutput += dataReceived; console.log(dataReceived)}}
    >
    {btnName}
    <div class="is-warning tag ld" >{pyProcesses.length || ""}</div>
</button>
