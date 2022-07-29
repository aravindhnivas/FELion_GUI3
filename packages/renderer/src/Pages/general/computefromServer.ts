import { pyServerPORT, get } from '../settings/svelteWritables'

interface Type {
    pyfile: string;
    args: Object;
    target?: HTMLButtonElement | null;
    general?: boolean;
}

export default async function ({ pyfile, args, target, general }: Type): Promise<DataFromPython | string | undefined> {
    try {
        console.time('Process Started')

        if (!general) {
            target?.classList.add('is-loading')
            const outputFile = window.path.join(window.appInfo.temp, 'FELion_GUI3', pyfile.split('.').at(-1) + '_data.json')
            if (window.fs.isFile(outputFile)) {
                const output = window.fs.removeSync(outputFile)
                if (window.fs.isError(output)) console.error(output)
            }
        }

        const URL = `http://localhost:${get(pyServerPORT)}/`

        const response = await fetch(URL, {
            method: 'POST',
            headers: { 'Content-type': 'application/json' },
            body: JSON.stringify({ pyfile, args: { ...args, general } }),
        })

        if (target?.classList.contains('is-loading')) {
            target.classList.remove('is-loading')
        }
        console.timeEnd('Process Started')
        
        console.warn(response)
        if (!response.ok) {
            const jsonErrorInfo = await response.json()
            console.log({ jsonErrorInfo })
            return Promise.reject(jsonErrorInfo?.error || jsonErrorInfo)
        }

        const dataFromPython = await response.json()
        if (!dataFromPython) return Promise.reject('could not get file from python. check the output json file')
        console.warn(dataFromPython)

        if (general) {
            const { done } = dataFromPython
            if (!done) Promise.reject(done)
            return Promise.resolve(<string>done)
        }

        return Promise.resolve(<DataFromPython>dataFromPython)
    } catch (error) {
        if (target?.classList.contains('is-loading')) {
            target.classList.remove('is-loading')
        }

        if(error instanceof Error) {
            const msg = error.message
            const details = error.stack || error
            console.error(error)
            return Promise.reject(new Error(`Error after receiving data from python \n${msg} \n${details}`))
        }
    
    }
}
