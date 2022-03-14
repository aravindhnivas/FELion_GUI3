
import Store from 'electron-store'
import { contextBridge } from 'electron'
import getPort from 'get-port';
import {portToPid} from 'pid-port'
import { kill as killPort, killer } from 'cross-port-killer';

const db = new Store({name: "db"});

const getPortId = async (port) => {

    try {

        const PID = await portToPid(parseInt(port))
        return Promise.resolve(PID)

    } catch (error) {
        console.warn(error)
        return Promise.resolve([])
    }

}

const getAvailablePort = async () => {

    try {

        const currentPORT = db.get("pyServerPORT") || ""
        const getpyServerPORT = await getPort({port: [currentPORT, 5050, 5353, 3000]})
        db.set("pyServerPORT", getpyServerPORT)
        console.log(`port ${getpyServerPORT} is open for starting pyServer`)

        console.log("page loading: closing felionpy server if it is running")

        const portsToClose = Array.from(new Set([currentPORT, getpyServerPORT]))
        const portsToCloseID = await Promise.all(portsToClose.map(async (p)=> await getPortId(p)))
        console.log({portsToClose, portsToCloseID})

        const pids = await killer.killByPid(portsToCloseID)
        console.warn("closing: ", pids)

        if(pids.length>0) {console.log("page loading: CLOSED - felionpy server if it is running")}

    } catch (error) {
    
        console.warn("Error occured while getting free port for pyServer")
        console.error(error)
    
    }
}
getAvailablePort()

contextBridge.exposeInMainWorld("getPort",
    (options={port: [db.get("pyServerPORT"), 5050, 5353, 3000]}) => getPort(options)
)


contextBridge.exposeInMainWorld("portToPid", getPortId)

contextBridge.exposeInMainWorld("killPort", (port) => killPort(port))
contextBridge.exposeInMainWorld("killByPid", (pid) => killer.killByPid(pid))
