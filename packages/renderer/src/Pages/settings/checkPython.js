import { pythonpath, pythonscript, pyVersion, developerMode, pyProgram, get } from './svelteWritables'

export async function resetPyConfig() {
    const pyPath = window.path.join(window.ROOT_DIR, 'python3/python')
    const pyScriptPath = window.path.join(window.ROOT_DIR, 'resources/python_files')

    window.db.set('pythonscript', pyScriptPath)
    pythonscript.set(window.db.get('pythonscript'))

    const [data, error] = await window.exec(`${pyPath} -V`)
    if (error) return window.handleError(error)

    pyVersion.set(data.stdout.trim())
    window.db.set('pythonpath', pyPath)
    pythonpath.set(pyPath)
    window.createToast('Location resetted', 'warning')
}

export async function updatePyConfig() {
    const [data, error] = await window.exec(`${get(pythonpath)} -V`)
    if (error) return window.handleError(error)

    pyVersion.set(data.stdout.trim())
    window.createToast('Location updated', 'success')

    window.db.set('pythonpath', get(pythonpath))
    window.db.set('pythonscript', get(pythonscript))
}

export async function getPyVersion(e) {

    e?.target?.classList.toggle('is-loading')

    const pyfile = 'getVersion'
    const pyArgs = get(developerMode) ? window.path.join(get(pythonscript), 'main.py') : ''

    const command = `${get(pyProgram)} ${pyArgs} ${pyfile} {} `
    const [{ stdout }, error] = await window.exec(command)
    
    if (error) {
        e?.target?.classList.toggle('is-loading')
        return Promise.reject(error)
    }

    const [version] = stdout?.split('\n').filter?.((line) => line.includes('Python')) || ['']
    pyVersion.set(version?.trim() || '')
    console.log({ stdout, version })

    window.db.set('pythonpath', get(pythonpath))
    window.db.set('pythonscript', get(pythonscript))
    window.db.set('pyVersion', get(pyVersion))

    window.createToast("python location updated", 'success')
    e?.target?.classList.toggle('is-loading')

    if (get(pyVersion)) return Promise.resolve(get(pyVersion))
}
