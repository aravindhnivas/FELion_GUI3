import { app, ipcMain } from 'electron'
import * as path from 'path'
import { promisify } from 'util'
import * as child from 'child_process';
import { db, ROOT_DIR } from './definedEnv'
import getPort from 'get-port'

const execCommand = promisify(child.exec)
const getCurrentDevStatus = () => {
    // if (!db.has('developerMode') || import.meta.env.PROD) {
    //     db.set('developerMode', false)
    // }

    const developerMode = <boolean>db.get('developerMode')
    const pythonscript = <string>db.get('pythonscript') || path.join(ROOT_DIR, 'resources/python_files')
    const pythonpath = <string>db.get('pythonpath') || path.join(ROOT_DIR, 'resources/python_files')
    
    let pyProgram
    const felionpy = <string>db.get('felionpy')
    if (app.isPackaged) {
        pyProgram = felionpy || path.join(ROOT_DIR, '../../', "resources/felionpy/felionpy")
    } else {
        pyProgram = developerMode ? pythonpath : felionpy
    }

    const mainpyfile = developerMode ? path.join(pythonscript, 'main.py') : ''

    return { db, developerMode, pyProgram, mainpyfile }
}
let pyVersion = ''

export async function getPyVersion() {
    try {
        const { pyProgram, mainpyfile } = getCurrentDevStatus()
        const pyfile = 'getVersion'

        const command = `${pyProgram} ${mainpyfile} ${pyfile} {} `

        console.info(command)
        const { stdout } = await execCommand(command)

        const [version] = stdout?.split('\n')?.filter?.((line) => line.includes('Python')) || ['']
        pyVersion = version?.trim() || ''
        console.log({ stdout, version })
        return Promise.resolve(pyVersion)
    } catch (error) {
        console.error('could not get python version', error)
        return Promise.resolve("")
    }
}

let py: child.ChildProcessWithoutNullStreams | undefined
let serverStarting = false

export async function startServer(webContents: Electron.WebContents) {
    
    if (serverStarting) return console.log('server already starting')

    const { db, developerMode, pyProgram, mainpyfile } = getCurrentDevStatus()

    const serverDebug = <boolean>db.get('serverDebug') ?? false
    const dbPORT = <number>db.get('pyServerPORT')
    const availablePORT = await getPort({ port: [5050, 5353, 3000, dbPORT] })

    console.log({ dbPORT, availablePORT })
    webContents?.send('db:update', {
        key: 'pyServerPORT',
        value: availablePORT,
    })

    console.info('starting felionpy server at port: ', availablePORT)

    return new Promise(async (resolve, reject) => {
        webContents?.send('db:update', { key: 'pyServerReady', value: false })
        webContents?.send('db:update', { key: 'pyVersion', value: pyVersion })

        if (!pyVersion) {
            pyVersion = await getPyVersion()
            if (!pyVersion) {
                console.error('Python is not valid. Fix it in Settings --> Configuration')
                reject('Python is not valid. Fix it in Settings --> Configuration')
                return
            }
        }
        console.log(pyVersion)
        webContents?.send('db:update', { key: 'pyVersion', value: pyVersion })

        const pyfile = 'server'
        const sendArgs = [pyfile, JSON.stringify({ port: availablePORT, debug: serverDebug })]
        const pyArgs = developerMode ? [mainpyfile, ...sendArgs] : sendArgs
        console.warn({ pyProgram, pyArgs })

        const opts = {}

        try {
            serverStarting = true
            const finalProgram = pyProgram.split(' ')
            const finalArgs = [...finalProgram.slice(1, ), ...pyArgs]

            console.warn(finalProgram[0], { finalArgs })
            py = child.spawn(finalProgram[0], finalArgs, opts)

            py.on('error', (error) => {
                webContents?.send('db:update', {
                    key: 'pyServerReady',
                    value: false,
                })
                serverStarting = false
                console.error('could not start felionpy server', error)
                reject(error)
            })

            py.on('spawn', () => {
                db.set('pyServerReady', true)
                webContents?.send('db:update', {
                    key: 'pyServerReady',
                    value: true,
                })
                console.info('pyServerReady', db.get('pyServerReady'))
                serverStarting = false
                resolve(true)
                console.log('server ready')
            })

            py.on('exit', () => {
                db.set('pyServerReady', false)
                serverStarting = false
                webContents?.send('db:update', {
                    key: 'pyServerReady',
                    value: false,
                })
                console.log('server closed')
            })

            py.stderr.on('data', (err) => {
                const stderr = String.fromCharCode.apply(null, err)
                console.warn("STDERR: ", stderr)
            })

            py.stdout.on('data', (data) => {
                const stdout = String.fromCharCode.apply(null, data)
                console.info("Server's stdout: ", stdout)
            })
        } catch (error) {
            serverStarting = false
            console.error(error, {serverStarting})
            webContents?.send('db:update', {
                key: 'pyServerReady',
                value: false,
            })
            reject(error)
        }
    })
}
ipcMain.on('stopServer', (_event, _args) => py?.kill?.())
