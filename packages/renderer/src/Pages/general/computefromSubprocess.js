import {
    pyProgram,
    pythonscript,
    get,
    pyVersion,
    pyServerReady,
    developerMode,
} from '../settings/svelteWritables'
import { running_processes } from '$src/svelteWritable'

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
    detached = null,
}) {
    return new Promise(async (resolve) => {
        let outputFile
        target ||= button || e?.target
        if (pyfile === 'server') {
            pyServerReady.set(false)
        }

        if (!general) {
            outputFile = pathJoin(
                appInfo.temp,
                'FELion_GUI3',
                pyfile.split('.').at(-1) + '_data.json'
            )
            if (fs.existsSync(outputFile)) {
                fs.removeSync(outputFile)
            }
            target?.classList.toggle('is-loading')
        }

        if (!get(pyVersion)) {
            window.handleError(
                'Python is not valid. Fix it in Settings --> Configuration'
            )
            return
        }

        console.info('Sending general arguments: ', args)
        window.createToast('Process Started')

        const sendArgs = [pyfile, JSON.stringify(args)]
        const mainPyFile = pathJoin(get(pythonscript), computepyfile + '.py')

        const pyArgs = get(developerMode) ? [mainPyFile, ...sendArgs] : sendArgs
        console.log(get(pyProgram), { pyArgs })

        const opts = { detached: detached !== null ? detached : general, shell }

        const py = spawn(get(pyProgram), pyArgs, opts)

        if (pyfile !== 'server') {
            running_processes.update((p) => [...p, { ...py, pyfile }])
        }
        py.on('error', (err) => {
            window.handleError(err)
            if (pyfile !== 'server') {
                running_processes.update((p) =>
                    p.filter((p) => p.pid !== py.pid)
                )
            }
            return
        })

        const logFile = pathJoin(
            appInfo.temp,
            'FELion_GUI3',
            pyfile + '_data.log'
        )
        const loginfo = fs.createWriteStream(logFile)

        let error = ''
        let dataReceived = ''

        dispatchEvent(target, { py, pyfile }, 'pyEvent')

        py.on('close', () => {
            if (pyfile === 'server') {
                pyServerReady.set(false)
            }

            dispatchEvent(
                target,
                { py, pyfile, dataReceived, error },
                'pyEventClosed'
            )
            if (pyfile !== 'server') {
                running_processes.update((p) =>
                    p.filter((p) => p.pid !== py.pid)
                )
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

            if (!fs.existsSync(outputFile)) {
                console.warn(`${outputFile} file doesn't exists`)
                window.handleError(`${outputFile} file doesn't exists`)
                return resolve(null)
            }

            const [dataFromPython] = fs.readJsonSync(outputFile)
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

            // console.log(`Output from python: ${dataReceived}`)
            console.log(dataString.trim())
            dispatchEvent(target, { py, pyfile, dataReceived }, 'pyEventData')
        })

        if (pyfile === 'server') {
            pyServerReady.set(true)
        }
    })
}
