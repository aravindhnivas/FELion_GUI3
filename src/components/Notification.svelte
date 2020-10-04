
<script>
    import { alert, defaultModules, Stack } from '@pnotify/core';
    import * as PNotifyMobile from '@pnotify/mobile';
    import '@pnotify/core/dist/Material.css';
    import {windowLoaded} from "../js/functions"
    defaultModules.set(PNotifyMobile, {});

    export let title="Notification", text = "Notice", type="info";

    function showStackTopLeft(type) {


        if (typeof window.stackTopLeft === 'undefined') {
            window.stackTopLeft = new Stack({
                dir1: 'down',

                dir2: 'right',
                firstpos1: 25,
                firstpos2: 25,
                push: 'top',
                maxStrategy: 'close',
                context: document.getElementById('Home')
            });
        }

        const opts = { title, text, stack: window.stackTopLeft };
        
        alert({...opts, type});
    }
    
    $: if($windowLoaded) {
        showStackTopLeft(type)
        showStackTopLeft(type)
        showStackTopLeft(type)
        showStackTopLeft(type)
    }

</script>