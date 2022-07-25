import { pyServerPORT, get } from './svelteWritables'

export const checkTCP = async ({ target = null, portNumber = get(pyServerPORT) }) => {
    try {
        target?.classList.toggle('is-loading')
        console.warn(`cheking TCP connection on port ${portNumber}`)
        if (!window.platform === 'win32') return Promise.resolve('')
        const command = `netstat -ano | findstr ${portNumber}`
        const results = await window.exec(command)
        return Promise.resolve(results)
    } catch (error) {
        return Promise.resolve(`>> ERROR: ${error.message}`)
    } finally {
        if (target?.classList.contains('is-loading')) {
            target?.classList.toggle('is-loading')
        }
    }
}

export const fetchServerROOT = async ({ target = null, portNumber = get(pyServerPORT) }) => {
    try {
        console.warn('fetching python server root')
        target?.classList.toggle('is-loading')
        const response = await fetch('http://localhost:' + portNumber)
        const textresponse = await response.text()
        return Promise.resolve(textresponse)
    } catch (error) {
        return Promise.resolve(`>> ERROR: ${error.message}`)
    } finally {
        if (target?.classList.contains('is-loading')) {
            target?.classList.toggle('is-loading')
        }
    }
}

export const isItfelionpy = async (portNumber = get(pyServerPORT)) => {
    const textresponse = await fetchServerROOT({ portNumber })
    if (textresponse?.includes('felionpy')) {
        return true
    }
    return false
}
