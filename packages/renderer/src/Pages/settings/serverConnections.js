
import {pyServerPORT, get} from "./svelteWritables"

export const checkTCP = async ()=>{
    console.warn(`cheking TCP connection on port ${get(pyServerPORT)}`)
    const results = await exec("netstat -ano | findstr " + get(pyServerPORT))
    console.log(results)
    return results
}

export const isportOpen = async () => {

    console.warn("Checking for existing connections")

    const [{stdout}, error] = await checkTCP()
    if(error) return Promise.reject(error)
    console.log(stdout)
    if(!stdout.includes("LISTENING")) return Promise.resolve(false)

    const PID = stdout?.split("LISTENING")[1]?.trim().split("\n")[0]?.trim()
    if(!PID) return Promise.reject("PID could not be found")

    console.warn("TCP running pid: ", PID)
    return Promise.resolve(PID)

}

export const fetchServerROOT = async ({target=null}={})=>{
    try {
        console.warn("fetching python server root")
        target?.classList.toggle("is-loading")
        const response = await fetch("http://localhost:" + get(pyServerPORT))
        const textresponse = await response.text()
        return Promise.resolve(textresponse)
    }
    catch (error) {return Promise.resolve(`>> ERROR: ${error.message}`)}
    finally {
        if(target?.classList.contains("is-loading")){
            target?.classList.toggle("is-loading")
        }
    }
}

export const isItfelionpy = async () => {
    const textresponse = await fetchServerROOT()
    if(textresponse?.includes("felionpy")) {
        return true
    }
    return false

}

export const closeConnection = async (PID) => {

    const [{stdout: closePIDOutput}, error1] = await exec("taskkill /F /PID " + PID)
    
    if(error1) {
        console.log("Error closing connection", error1)
        return Promise.reject(error1)
    }

    console.log(closePIDOutput)
    return Promise.resolve(closePIDOutput)
}