import { writable, get } from 'svelte/store'
import { uniqBy } from 'lodash-es'

export const customStore = <T>(defaultValue: T) => {
    const store = writable<{ [key: string]: T }>({})
    const { subscribe, set, update } = store

    return {
        subscribe,
        set,
        get: (key: string) => {
            return get(store)[key]
        },
        update: (key: string, value: T, uniq: string = '') => {
            update((data) => {
                const oldValue = data[key]
                let newValue
                if (Array.isArray(oldValue)) {
                    newValue = [...oldValue, value]
                    if (uniq) {
                        newValue = uniqBy(newValue, uniq)
                    }
                } else {
                    newValue = value
                }
                data[key] = newValue
                return data
            })
        },
        setValue: (key: string, value: T) => {
            update((data) => {
                data[key] = value
                return data
            })
        },
        init: (key: string) => {
            update((data) => {
                data[key] = defaultValue
                return data
            })
        },
        remove: (key: string) => {
            update((data) => {
                delete data[key]
                return data
            })
        },
    }
}

export const getfiles = (location: string, filter: string) => {
    if (!window.fs.isDirectory(location)) return [{ name: '', id: window.getID() }]
    return window.fs
        .readdirSync(location)
        .filter((f) => f.endsWith(filter))
        .map((f) => ({ name: f, id: window.getID() }))
}
