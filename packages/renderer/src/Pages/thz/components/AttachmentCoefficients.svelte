
<script>

    import Textfield        from '@smui/textfield';
    import {cloneDeep}      from "lodash-es"
    import CustomTextSwitch from "$components/CustomTextSwitch.svelte";
    export let numberDensity;
    export let attachmentCoefficients=[]
    export let k3={constant:[], rate:[]}
    export let kCID={constant:[], rate:[]}

    const computeAttachmentRate = () => {

        k3.rate = cloneDeep(k3.constant).map(
            (rate) => ({...rate, value: Number(rate.value*numberDensity**2).toFixed(3), id:getID() })
        );
    
        kCID.rate = cloneDeep(kCID.constant).map(
            (rate) => ({...rate, value: Number(rate.value*numberDensity).toFixed(3), id:getID() })
        );
    }
    $: if(numberDensity) {
        computeAttachmentRate()
    }

</script>

<div class="sub_container__div box">

    <div class="subtitle">Rare-gas attachment (K3) and dissociation (kCID) constants</div>

    <div class="content__div">
        {#each attachmentCoefficients as {label, value, id}(id)}
            <CustomTextSwitch bind:value {label} step={0.1} />
        {/each}

        <div class="align h-center">
            <Textfield bind:value={numberDensity} label="numberDensity (cm-3)"/>
            <button class="button is-link" on:click={computeAttachmentRate}>Compute rate constants</button>

            <div class="align h-center" >
                <div class="">k3 (cm6/s): </div>
                {#each k3.constant as {label, value, id} (id)}
                    <Textfield bind:value {label}  />

                {/each}
                
            </div>

            <div class="align h-center">

                <div class="">kCID  (cm3/s): </div>
                {#each kCID.constant as {label, value, id} (id)}

                    <Textfield bind:value {label}  />
                {/each}
            </div>

            <hr>

            <div class="align h-center">
                <div class="">k3 (per sec): </div>

                {#each k3.rate as {label, value, id} (id)}
                    <Textfield bind:value {label} />
                {/each}
            </div>

            <div class="align h-center">

                <div class="">kCID (per sec): </div>
                {#each kCID.rate as {label, value, id} (id)}

                    <Textfield bind:value {label}  />
                {/each}
            </div>
        </div>
    
    </div>

</div>


<style lang="scss">
    .sub_container__div {
        display: grid;
        grid-row-gap: 1em;
        .subtitle {place-self:center;}

        .content__div {
            max-height: 30rem;

            overflow-y: auto;
            display: flex;
            flex-wrap: wrap;
            justify-self: center; // grow from center (width is auto adjusted)
            gap: 1em;
            justify-content: center; // align items center
        }
        
    }

    hr {background-color: #fafafa; margin: 0;}
</style>