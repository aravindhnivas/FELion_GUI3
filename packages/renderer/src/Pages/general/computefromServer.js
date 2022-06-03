import { pyServerPORT, get } from '../settings/svelteWritables'
export default async function ({ target = null, general = false, pyfile, args }) {
    try {
        console.time('Process Started')
        // window.createToast("Process Started", "warning")

        if (!general) target?.classList.add('is-loading')

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
        // window.createToast("Process completed", "success")
        // const response = await responsePromise
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
            return Promise.resolve(done)
        }

        return Promise.resolve(dataFromPython)
    } catch (error) {
        if (target?.classList.contains('is-loading')) {
            target.classList.remove('is-loading')
        }
        const msg = error.message
        const details = error.stack || error
        console.error(error)
        return Promise.reject(`Error after receiving data from python \n${msg} \n${details}`)
    }
}
