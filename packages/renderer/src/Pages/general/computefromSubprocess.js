import { pyProgram, pythonscript, get, pyVersion, pyServerReady, developerMode } from '../settings/svelteWritables'
import { running_processes } from '$src/sveltewritables'

export const dispatchEvent = (target, detail, eventName) => {
    const pyEventClosed = new CustomEvent(eventName, { bubbles: false, detail })
    target?.dispatchEvent(pyEventClosed)
    console.info(eventName + ' dispatched')
}

export default async function ({
    e = null,
    target = null,
    button = null,
    general = false,
    pyfile,
    args,
    computepyfile = 'main',
    shell = false,
    detached = false,
}) {
    return new Promise((resolve) => {
        let outputFile
        target ||= button || e?.target
        if (pyfile === 'server') {
            pyServerReady.set(false)
        }

        if (!general) {
            outputFile = window.path.join(window.appInfo.temp, 'FELion_GUI3', pyfile.split('.').at(-1) + '_data.json')
            if (window.fs.existsSync(outputFile)) {
                window.fs.removeSync(outputFile)
            }
            target?.classList.toggle('is-loading')
        }

        if (!get(pyVersion)) {
            window.handleError('Python is not valid. Fix it in Settings --> Configuration')
            return
        }

        console.info('Sending general arguments: ', args)
        window.createToast('Process Started')

        const sendArgs = [pyfile, JSON.stringify(args)]
        const mainPyFile = window.path.join(get(pythonscript), computepyfile + '.py')

        const finalProgram = get(pyProgram).split(' ')
        const pyArgs = get(developerMode) ? [mainPyFile, ...sendArgs] : sendArgs

        const finalArgs = [...finalProgram.slice(1, ), ...pyArgs]
        console.warn(finalProgram[0], { finalArgs })

        const opts = { detached, shell }
        const py = window.spawn(finalProgram[0], finalArgs, opts)
        if (pyfile !== 'server') {
            running_processes.update((p) => [
                ...p,
                {
                    pid: py.pid,
                    pyfile, 
                    close: {
                        name: 'X', 
                        cb: () => py.kill(),
                        style: 'background: var(--color-danger); cursor: pointer; color: var(--color-white);',
                    } 
                }
            ])
        }

        py.on('error', (err) => {
            window.handleError(err)

            if (pyfile !== 'server') {
                running_processes.update((p) => p.filter((p) => p.pid !== py.pid))
            }
            return
        })

        const logFile = window.path.join(window.appInfo.temp, 'FELion_GUI3/logs', pyfile + '_data.log')
        const loginfo = window.fs.createWriteStream(logFile)

        let error = ''
        let dataReceived = ''
        dispatchEvent(target, { py, pyfile }, 'pyEvent')

        py.on('close', () => {
            if (pyfile === 'server') {
                pyServerReady.set(false)
            }

            dispatchEvent(target, { py, pyfile, dataReceived, error }, 'pyEventClosed')
            if (pyfile !== 'server') {
                running_processes.update((p) => p.filter((p) => p.pid !== py.pid))
            }

            if (error) {
                resolve(null)
                loginfo.write(`\n\n[ERROR OCCURED]\n${error}\n`)
                loginfo.end()

                if (error.includes('Traceback')) {
                    return window.handleError(error)
                }
                return console.error(error)
            }

            if (general) {
                return resolve(dataReceived)
            }

            if (!window.fs.existsSync(outputFile)) {
                console.warn(`${outputFile} file doesn't exists`)
                window.handleError(`${outputFile} file doesn't exists`)
                return resolve(null)
            }

            const [dataFromPython] = window.fs.readJsonSync(outputFile)
            resolve(dataFromPython)

            if (target?.classList.contains('is-loading')) {
                target.classList.remove('is-loading')
            }
            console.info('Process closed')
        })

        py.stderr.on('data', (err) => {
            const errorString = `${String.fromCharCode.apply(null, err)}\n`
            if (pyfile === 'server') {
                error = errorString
            } else {
                error += errorString
            }
            dispatchEvent(target, { py, pyfile, error }, 'pyEventStderr')
            console.log(`Output from python: ${errorString}`)
        })

        py.stdout.on('data', (data) => {
            loginfo.write(data)
            const dataString = `${String.fromCharCode.apply(null, data)}\n`
            if (pyfile === 'server') {
                dataReceived = dataString
            } else {
                dataReceived += dataString
            }
            console.log(dataString.trim())
            dispatchEvent(target, { py, pyfile, dataReceived }, 'pyEventData')
        })

        if (pyfile === 'server') {
            pyServerReady.set(true)
        }
    })
}
