import { pythonscript, pyVersion, developerMode, pyProgram, get } from './svelteWritables'

export async function getPyVersion(e?: ButtonClickEvent) {

    const target = e?.target as HTMLButtonElement
    target?.classList.toggle('is-loading')

    const pyfile = 'getVersion'
    const pyArgs = get(developerMode) ? window.path.join(get(pythonscript), 'main.py') : ''

    const command = `${get(pyProgram)} ${pyArgs} ${pyfile} {} `

    const data = await window.exec(command)
    if (data instanceof Error) {
        target?.classList.toggle('is-loading')
        return Promise.resolve(data)
    }
    const { stdout } = data
    const [version] = stdout?.split('\n').filter?.((line) => line.includes('Python')) || ['']
    pyVersion.set(version?.trim() || '')
    console.log({ stdout, version })
    window.createToast("python location updated", 'success')
    target?.classList.toggle('is-loading')
    return Promise.resolve(get(pyVersion))

}
