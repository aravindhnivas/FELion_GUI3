
import Store from 'electron-store'
import { contextBridge } from 'electron'
import getPort from 'get-port';
import { kill as killPort, killer } from 'cross-port-killer';
const pids = require("find-pid-from-port")

const db = new Store({name: "db"});

const getAvailablePort = async () => {
    
    try {
    
        const pyServerPORT = await getPort({port: [3000, 5050, 5353]})
        db.set("pyServerPORT", pyServerPORT)
        console.log(`port ${pyServerPORT} is open for starting pyServer`)

    } catch (error) {
    
        console.warn("Error occured while getting free port for pyServer")
        console.error(error)
    
    }
}
getAvailablePort()

contextBridge.exposeInMainWorld("getPort", (options={port: [db.get("pyServerPORT"), 5050, 5353, 3000]}) => getPort(options))
contextBridge.exposeInMainWorld("getpids", (port) => pids(port))
contextBridge.exposeInMainWorld("killPort", (port) => killPort(port))
contextBridge.exposeInMainWorld("killByPid", (pid) => killer.killByPid(pid))
