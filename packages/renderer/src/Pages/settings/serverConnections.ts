import { pyServerPORT, get } from './svelteWritables'

type Target = EventTarget & HTMLButtonElement
type Type = {target?: Target, portNumber?: number}

export const checkTCP = async ({ target, portNumber = get(pyServerPORT) }: Type) => {
    target?.classList.toggle('is-loading')
    console.warn(`cheking TCP connection on port ${portNumber}`)

    if (window.platform !== 'win32') return Promise.resolve({stdout: '', stderr: ''})

    const command = `netstat -ano | findstr ${portNumber}`

    const data = await window.exec(command)

    if (data instanceof Error) {
        target?.classList.toggle('is-loading')
        return Promise.resolve(data)
    }
    
    target?.classList.toggle('is-loading')
    return Promise.resolve(data)
}

export const fetchServerROOT = async ({ target, portNumber = get(pyServerPORT) }: Type) => {
    console.warn('fetching python server root')
    target?.classList.toggle('is-loading')
    try {
        const response = await fetch(`http://localhost:${portNumber}/`)
        const textresponse = await response.text()
        return Promise.resolve(textresponse)
    } catch (error) {
        if(error instanceof Error) {
            return Promise.resolve(error)
        } else {
            return Promise.resolve(new Error(error as string))
        }
    } finally {
        target?.classList.toggle('is-loading')
    }
    
}

export const isItfelionpy = async (portNumber: number = get(pyServerPORT)) => {
    const textresponse = await fetchServerROOT({ portNumber })
    return textresponse instanceof Error ? false : textresponse.includes('felionpy')
}
