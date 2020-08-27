
<script>
    import Modal from '../../../components/Modal.svelte';
    import FelixPlotWidgets from './FelixPlotWidgets.svelte';
    import CustomCheckList from '../../../components/CustomCheckList.svelte';
    import Textfield from '@smui/textfield';
    import CustomCheckbox from '../../../components/CustomCheckbox.svelte';
    
    import {loadfile, savefile} from "../functions/misc"
    import { createEventDispatcher } from 'svelte';
    import FelixPlotExtraWidgets from './FelixPlotExtraWidgets.svelte';
    export let active=false, felixPlotWidgets = {}, felixPlotCheckboxes;

    const dispatch = createEventDispatcher();

    let extraWidgetCollection = {text:[], number:[], boolean:[]}

    let extraWidget={ label:"", value:"", step:"" }
    
    let extraWidgetModal = false, widgetType = ""

    const widgetLocation = path.resolve(__dirname, "config")
    const widgetFile = "felixplotWidgets"

    function saveWidget(){ savefile({file:extraWidgetCollection, name:widgetFile, location:widgetLocation}) }
    
    function loadExtraWidgets() { 

        const loadedContent = loadfile({name:widgetFile, location:widgetLocation})

        if(!loadedContent) {
            extraWidgetCollection = loadedContent
            felixPlotWidgets.text = [...felixPlotWidgets.text, extraWidgetCollection.text]
            felixPlotWidgets.number = [...felixPlotWidgets.number, extraWidgetCollection.number]

            felixPlotWidgets.boolean = [...felixPlotWidgets.boolean, extraWidgetCollection.boolean]
        
        }
    
    }

    const addExtraWidget = (event) => {  widgetType = event.detail.type; extraWidgetModal = true; }

    
    const widgetAdded =  () => {

        extraWidget.id = window.getID()
        felixPlotWidgets[widgetType] = [...felixPlotWidgets[widgetType], extraWidget]
    
        console.log(felixPlotWidgets[widgetType])
        extraWidgetCollection[widgetType] = [...extraWidgetCollection[widgetType], extraWidget]
        extraWidget={label:"", value:"", step:""}
    
        extraWidgetModal = false
    
    }
</script>

{#if active}

    <Modal bind:active title="FELIX PLOTTING">

        <div slot="content" style="height:40vh;" use:loadExtraWidgets>

            <FelixPlotWidgets bind:felixPlotWidgets bind:felixPlotCheckboxes on:addWidget={addExtraWidget}/>
        </div>

        <div class="" slot="footerbtn">

            <button class="button is-link" on:click={saveWidget}>Save Widgets</button>
    
            <button class="button is-link" on:click={(e)=>{dispatch('submit', {event:e})}} >Submit</button>
        
        </div>
    </Modal>

{/if}

<FelixPlotExtraWidgets bind:active={extraWidgetModal} bind:extraWidget {widgetType} on:widgetadded={widgetAdded}/>