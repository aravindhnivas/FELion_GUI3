import { app, ipcMain, webContents } from 'electron'
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
// db.onDidChange('pyServerReady', (value) => {
//     console.info('pyServerReady', value)
// })

const spawnServer = (webContents: Electron.WebContents) => {
    console.info('pyServerReady', db.get('pyServerReady'))
    webContents?.send('db:update', {
        key: 'pyServerReady',
        value: true,
    })
    serverStarting = false
    console.log('server ready')
}

const closeServer = (webContents: Electron.WebContents) => {
    console.info('pyServerReady', db.get('pyServerReady'))
    webContents?.send('db:update', {
        key: 'pyServerReady',
        value: false,
    })
    serverStarting = false
    console.log('server closed')
}
const handleServerError = (error: Error | string, webContents: Electron.WebContents) => {
    console.error('server error\n', error)
    closeServer(webContents)
}

export async function startServer(webContents: Electron.WebContents) {

    if (serverStarting) {
        console.log('server already starting')
        return Promise.resolve(false)
    }

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
            if (!pyVersion) return reject('could not get python version')
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
                handleServerError(error, webContents)
                reject(error)
            })

            py.on('spawn', () => {
                spawnServer(webContents)
                resolve(true)
            })

            py.on('exit', () => closeServer(webContents))

            py.stderr.on('data', (err) => {
                const stderr = String.fromCharCode.apply(null, err)
                console.warn("STDERR: ", stderr)
            })

            py.stdout.on('data', (data) => {
                const stdout = String.fromCharCode.apply(null, data)
                console.info("Server's stdout: ", stdout)
            })

        } catch (error) {
            handleServerError(<Error>error, webContents)
            reject(error)
        }
    })
}
ipcMain.on('stopServer', (_event, _args) => py?.kill?.())
