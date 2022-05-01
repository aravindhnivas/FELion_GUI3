<script>
    import { difference } from 'lodash-es'

    export let pyProcesses = []
    export let btnName = 'Submit'
    export let stdOutput = ''
    export let stderr = ''
    export let disabled = false
    export let id = getID()
</script>

<button
    {id}
    class="button is-link ld-ext-right"
    {disabled}
    class:running={pyProcesses.length > 0}
    on:click
    on:pyEvent={({ detail: { py } }) => {
        pyProcesses = [...pyProcesses, py]
        stdOutput = ''
    }}
    on:pyEventClosed={({ detail: { py } }) => {
        pyProcesses = difference(pyProcesses, [py])
    }}
    on:pyEventData={({ detail: { dataReceived } }) => {
        stdOutput += dataReceived
    }}
    on:pyEventStderr={({ detail: { error } }) => {
        stderr += error
        console.warn(error)
    }}
>
    {btnName}
    <div class="is-warning tag ld">{pyProcesses.length || ''}</div>
</button>
