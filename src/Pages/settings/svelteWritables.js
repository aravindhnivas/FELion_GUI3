
import { writable, derived, get } from "svelte/store";
export { get };

export const github = writable({ branch: "master", repo: "FELion_GUI3", username: "aravindhnivas" })
export const versionJson = derived(github, ($github) => `https://raw.githubusercontent.com/${$github.username}/${$github.repo}/${$github.branch}/version.json`)
export const urlzip = derived(github, ($github) => `https://codeload.github.com/${$github.username}/${$github.repo}/zip/${$github.branch}`)

export const pythonpath = writable(localStorage["pythonpath"] || path.resolve(__dirname, "../python3/python"))

export const pythonscript = writable(localStorage["pythonscript"] || path.resolve(__dirname, "assets/python_files"))
export const pyVersion = writable("")

if (!localStorage["pythonpath"]) localStorage["pythonpath"] = get(pythonpath)

if (!localStorage["pythonscript"]) localStorage["pythonscript"] = get(pythonpath)

export const backupName = writable("FELion_GUI_backup")