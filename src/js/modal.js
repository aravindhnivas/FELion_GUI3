
import * as PNotify from '@pnotify/core';
import * as PNotifyMobile from '@pnotify/mobile';
import * as PNotifyFontAwesome5Fix from '@pnotify/font-awesome5-fix';
import * as PNotifyFontAwesome5 from '@pnotify/font-awesome5';

PNotify.defaultModules.set(PNotifyFontAwesome5Fix, {});
PNotify.defaultModules.set(PNotifyFontAwesome5, {});
PNotify.defaultModules.set(PNotifyMobile, {});

window.showStackContext = ({title="Info", text, type="Info"}={}) => {
    if (typeof window.stackContext === 'undefined') {

        window.stackContext = new PNotify.Stack({
            dir1: 'down',
            dir2: 'left',
            firstpos1: 70,
            firstpos2: 25,


            hide: false,
            context: document.getElementById('pageContainer')
        });
    }
    const opts = {

        title, text, type,

        stack: window.stackContext
    };
    PNotify.notice(opts);
}