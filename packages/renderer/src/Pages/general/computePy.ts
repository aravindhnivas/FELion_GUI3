import computefromServer from './computefromServer'
import computefromSubprocess from './computefromSubprocess'
import { pyServerReady, get, developerMode, pyProgram } from '../settings/svelteWritables'


interface Type {
    pyfile: string;
    args: Object;
    target?: HTMLButtonElement | null;
    general?: boolean;
    e?: Event;
}

const restartServer = async () => {
    const restartPyServer = await window.dialogs.showMessageBox({
        message: 'Restart Python server?',
        title: 'Python server is not ready',
        type: 'warning',
        buttons: ['Ok', 'Cancel'],
    })

    if (restartPyServer.response == 1) return Promise.resolve(null)

    const serverSpawned = await window.startServer()
    if (!serverSpawned) {
        window.handleError('Python server is not ready. Fix it in Settings --> Configuration')
        return Promise.resolve(null)
    }
    window.createToast('Python server is ready')
    return Promise.resolve(true)
}
export default async function ({ e, target, pyfile, args, general}: Type) {
    
    target ||= e?.target as HTMLButtonElement
    let dataFromPython: DataFromPython | string | undefined
    let processDivGeneral
    let processDivGeneralNum = 0

    try {

        console.log(`Running python in ${general ? 'subprocess' : 'server'} mode`)
        console.warn(`Running python in ${get(developerMode) ? 'developer' : 'production'} mode \n ${get(pyProgram)}`)

        if (!get(pyServerReady)) {
            await window.sleep(2000)
            if (!get(pyServerReady)) {
                const ready = await restartServer()
                if (!ready) return Promise.resolve(null)
            }
        }

        console.warn({ pyfile, args, general })
        if (general) {
            if (target) {
                processDivGeneral = target.getElementsByClassName('tag')?.[0]
                console.log(processDivGeneral)
                if(processDivGeneral) {
                    const num = processDivGeneral.textContent as string
                    processDivGeneralNum = isNaN(parseInt(num)) ? 0 : parseInt(num)
                    processDivGeneral.textContent = `${processDivGeneralNum + 1}`
                }
                
            }
            dataFromPython = await computefromSubprocess({
                target,
                general,
                pyfile,
                args,
            })
            
        } else {
            dataFromPython = await computefromServer({
                target,
                general,
                pyfile,
                args,
            })
        }

        return Promise.resolve(dataFromPython)
    } catch (error) {
        window.handleError(error)

    } finally {
        if (processDivGeneral) {
            const num = processDivGeneral.textContent as string
            processDivGeneralNum = isNaN(parseInt(num)) ? 0 : parseInt(num)
            const currentNum = processDivGeneralNum - 1

            if (currentNum > 0) {
                processDivGeneral.textContent = `${currentNum}`
            } else {
                processDivGeneral.textContent = ''
            }
        }
        console.log('COMPLETED')
    }
}
