import { createServer, build, createLogger, LogLevel, InlineConfig, ViteDevServer } from 'vite'
import electronPath from 'electron'
import { ChildProcessWithoutNullStreams, spawn } from 'child_process'

/** @type 'production' | 'development'' */
const mode = (process.env.MODE = process.env.MODE || 'development')

const LOG_LEVEL: LogLevel = 'info'

const sharedConfig: InlineConfig = {
    mode,
    build: {
        watch: {},
    },
    logLevel: LOG_LEVEL,
}

/** Messages on stderr that match any of the contained patterns will be stripped from output */
const stderrFilterPatterns = [
    // warning about devtools extension
    // https://github.com/cawa-93/vite-electron-builder/issues/492
    // https://github.com/MarshallOfSound/electron-devtools-installer/issues/143
    /ExtensionLoadWarning/,
]

/**
 *
 * @param {{name: string; configFile: string; writeBundle: import('rollup').OutputPlugin['writeBundle'] }} param0
 * @returns {import('rollup').RollupWatcher}
 */
const getWatcher = ({
    name,
    configFile,
    writeBundle,
}: {
    name: string
    configFile: string
    writeBundle: import('rollup').OutputPlugin['writeBundle']
}) => {
    return build({
        ...sharedConfig,
        configFile,
        plugins: [{ name, writeBundle }],
    })
}

const setupMainPackageWatcher = (viteDevServer: ViteDevServer) => {
    // Write a value to an environment variable to pass it to the main process.
    {
        const protocol = `http${viteDevServer.config.server.https ? 's' : ''}:`
        const host = viteDevServer.config.server.host || 'localhost'
        const port = viteDevServer.config.server.port // Vite searches for and occupies the first free port: 3000, 3001, 3002 and so on
        const path = '/'
        process.env.VITE_DEV_SERVER_URL = `${protocol}//${host}:${port}${path}`
        console.log(process.env.VITE_DEV_SERVER_URL)
    }

    const logger = createLogger(LOG_LEVEL, {
        prefix: '[main]',
    })

    let spawnProcess: ChildProcessWithoutNullStreams | null = null

    return getWatcher({
        name: 'reload-app-on-main-package-change',
        configFile: 'packages/main/vite.config.js',
        writeBundle() {
            if (spawnProcess !== null) {
                spawnProcess.kill('SIGINT')
                spawnProcess = null
            }

            spawnProcess = spawn(String(electronPath), ['.'])

            spawnProcess.stdout.on('data', (d) => d.toString().trim() && logger.warn(d.toString(), { timestamp: true }))
            spawnProcess.stderr.on('data', (d) => {
                const data = d.toString().trim()
                if (!data) return
                const mayIgnore = stderrFilterPatterns.some((r) => r.test(data))
                if (mayIgnore) return
                logger.error(data, { timestamp: true })
            })
        },
    })
}

const setupPreloadPackageWatcher = (viteDevServer: ViteDevServer) => {
    return getWatcher({
        name: 'reload-page-on-preload-package-change',
        configFile: 'packages/preload/vite.config.js',
        writeBundle() {
            viteDevServer.ws.send({
                type: 'full-reload',
            })
        },
    })
}

;(async () => {
    try {
        const viteDevServer = await createServer({
            ...sharedConfig,
            configFile: 'packages/renderer/vite.config.js',
        })
        await viteDevServer.listen()

        await setupPreloadPackageWatcher(viteDevServer)
        await setupMainPackageWatcher(viteDevServer)
    } catch (e) {
        console.error(e)
        process.exit(1)
    }
})()
