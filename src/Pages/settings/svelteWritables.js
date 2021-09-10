
import { writable, derived, get } from "svelte/store";
export { get };
export const github = writable({ branch: "master", repo: "FELion_GUI3", username: "aravindhnivas" })
export const githubRepo = derived(github, ($github) => `https://raw.githubusercontent.com/${$github.username}/${$github.repo}/${$github.branch}`)
export const versionJson = derived(githubRepo, ($githubRepo) => `${$githubRepo}/version.json`)
export const urlzip = derived(github, ($github) => `https://codeload.github.com/${$github.username}/${$github.repo}/zip/${$github.branch}`)

if (!db.get("pythonpath")) db.set("pythonpath", path.resolve(__dirname, "../python3/python"))
if (!db.get("pythonscript")) db.set("pythonscript", path.resolve(__dirname, "assets/python_files"))
export const pythonpath = writable(db.get("pythonpath"))
export const pythonscript = writable(db.get("pythonscript"))

export const pyVersion = writable("")

export const backupName = writable("FELion_GUI_backup")

export const developerMode = writable(versionFileJSON.developer)


export const suppressInitialDeveloperWarning = writable(db.get("suppressInitialDeveloperWarning") || false)