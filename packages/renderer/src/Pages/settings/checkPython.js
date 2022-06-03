import { pythonpath, pythonscript, pyVersion, developerMode, pyProgram, get } from './svelteWritables'

export async function resetPyConfig() {
    const pyPath = window.path.join(ROOT_DIR, 'python3/python')
    const pyScriptPath = window.path.join(ROOT_DIR, 'resources/python_files')

    db.set('pythonscript', pyScriptPath)
    pythonscript.set(db.get('pythonscript'))

    const [data, error] = await window.exec(`${pyPath} -V`)
    if (error) return window.handleError(error)

    pyVersion.set(data.stdout.trim())
    db.set('pythonpath', pyPath)
    pythonpath.set(pyPath)
    window.createToast('Location resetted', 'warning')
}

export async function updatePyConfig() {
    const [data, error] = await window.exec(`${get(pythonpath)} -V`)
    if (error) return window.handleError(error)

    pyVersion.set(data.stdout.trim())
    window.createToast('Location updated', 'success')

    db.set('pythonpath', get(pythonpath))
    db.set('pythonscript', get(pythonscript))
}

export async function getPyVersion(e) {
    e?.target?.classList.toggle('is-loading')

    const pyfile = 'getVersion'
    const pyArgs = get(developerMode) ? window.path.join(get(pythonscript), 'main.py') : ''

    const command = `${get(pyProgram)} ${pyArgs} ${pyfile} {} `
    const [{ stdout }, error] = await window.exec(command)
    if (error) return Promise.reject(error)

    const [version] = stdout?.split('\n').filter?.((line) => line.includes('Python')) || ['']
    pyVersion.set(version?.trim() || '')
    console.log({ stdout, version })

    e?.target?.classList.toggle('is-loading')
    if (get(pyVersion)) return Promise.resolve(get(pyVersion))
}
