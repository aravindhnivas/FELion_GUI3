import { pythonpath, pythonscript, pyVersion, developerMode, pyProgram, get } from './svelteWritables'

export async function resetPyConfig() {
    const pyPath = window.path.join(window.ROOT_DIR, 'python3/python')
    const pyScriptPath = window.path.join(window.ROOT_DIR, 'resources/python_files')
    
    pythonscript.set(pyScriptPath)
    const [,error] = await window.exec(`${pyPath} -V`)
    if (error instanceof Error) return window.handleError(error)
    pythonpath.set(pyPath)
    window.createToast('Location resetted', 'warning')
}

export async function getPyVersion(e: ButtonClickEvent) {

    const target = e?.target as HTMLButtonElement
    target?.classList.toggle('is-loading')

    const pyfile = 'getVersion'
    const pyArgs = get(developerMode) ? window.path.join(get(pythonscript), 'main.py') : ''

    const command = `${get(pyProgram)} ${pyArgs} ${pyfile} {} `
    const computedOutput = await window.exec(command)
    if(computedOutput === undefined) return window.handleError(new Error('Could not get python version'))

    const [data, error] = await window.exec(command)

    if (error instanceof Error) {
        target?.classList.toggle('is-loading')
        return Promise.reject(error)
    }

    const { stdout } = data as { stdout: string, stderr: string }

    const [version] = stdout?.split('\n').filter?.((line) => line.includes('Python')) || ['']
    pyVersion.set(version?.trim() || '')
    console.log({ stdout, version })

    window.createToast("python location updated", 'success')
    target?.classList.toggle('is-loading')
    if (get(pyVersion)) return Promise.resolve(get(pyVersion))

}
