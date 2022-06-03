import computefromServer from './computefromServer'
import computefromSubprocess from './computefromSubprocess'
import { pyServerReady, get } from '../settings/svelteWritables'

export default async function ({ e = null, target = null, pyfile = '', args = {}, general = false } = {}) {
    target ||= e?.target
    let dataFromPython = null
    let processDivGeneral
    let processDivGeneralNum = 0

    try {
        if (!get(pyServerReady)) {
            const restartPyServer = await dialogs.showMessageBox({
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
        }

        console.log({ pyfile, args, general })
        if (general) {
            // console.info(target)
            if (target) {
                processDivGeneral = target.getElementsByClassName('tag')
                if (processDivGeneral.length === 0) {
                    processDivGeneral = document.createElement('span')
                    processDivGeneral.className = 'tag__span tag is-warning hide'
                    processDivGeneral.textContent = '1'
                    target.appendChild(processDivGeneral)
                } else {
                    processDivGeneral = processDivGeneral[0]
                    const num = processDivGeneral.textContent
                    processDivGeneralNum = isNaN(parseInt(num)) ? 0 : parseInt(num)
                    processDivGeneral.textContent = `${processDivGeneralNum + 1}`
                }
                if (processDivGeneral.classList.contains('hide')) {
                    processDivGeneral.classList.remove('hide')
                }
                // console.log(processDivGeneral)
            }
            dataFromPython = await computefromSubprocess({
                target,
                general,
                pyfile,
                args,
            })
            return
        }

        dataFromPython = await computefromServer({
            target,
            general,
            pyfile,
            args,
        })
    } catch (error) {
        window.handleError(error)
    } finally {
        if (processDivGeneral) {
            const num = processDivGeneral.textContent
            processDivGeneralNum = isNaN(parseInt(num)) ? 0 : parseInt(num)
            const currentNum = processDivGeneralNum - 1

            if (currentNum > 0) {
                processDivGeneral.textContent = `${currentNum}`
            } else {
                if (pyfile.includes('baseline')) {
                    processDivGeneral.textContent = 'b'
                } else {
                    processDivGeneral.textContent = ''
                    processDivGeneral.classList.add('hide')
                }
            }
        }
        console.log('COMPLETED')
        return Promise.resolve(dataFromPython)
    }
}
