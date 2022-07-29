import { pyServerPORT, get } from './svelteWritables'

type Target = EventTarget & HTMLButtonElement
type Type = {target?: Target, portNumber: number}

export const checkTCP = async ({ target, portNumber = get(pyServerPORT) }: Type) => {

    try {
        target?.classList.toggle('is-loading')
        console.warn(`cheking TCP connection on port ${portNumber}`)
        if (window.platform !== 'win32') return Promise.resolve('')
        const command = `netstat -ano | findstr ${portNumber}`
        const results = await window.exec(command)
        return Promise.resolve(results)

    } catch (error) {
        if(error instanceof Error) {
            return Promise.resolve(`>> ERROR: ${error.message}`)
        }
    } finally {
        if (target?.classList.contains('is-loading')) {
            target?.classList.toggle('is-loading')
        }
    }
}

export const fetchServerROOT = async ({ target, portNumber = get(pyServerPORT) }: Type) => {
    try {
        console.warn('fetching python server root')
        target?.classList.toggle('is-loading')
        const response = await fetch('http://localhost:' + portNumber)
        const textresponse = await response.text()
        return Promise.resolve(textresponse)
    } catch (error) {
        if(error instanceof Error) {
            return Promise.resolve(`>> ERROR: ${error.message}`)
        }
    } finally {
        if (target?.classList.contains('is-loading')) {
            target?.classList.toggle('is-loading')
        }
    }
}

export const isItfelionpy = async (portNumber: number = get(pyServerPORT)) => {
    const textresponse = await fetchServerROOT({ portNumber })
    if (textresponse?.includes('felionpy')) {
        return true
    }
    return false
}
