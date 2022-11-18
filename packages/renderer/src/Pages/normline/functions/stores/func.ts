import { writable } from 'svelte/store'
import { uniqBy } from 'lodash-es'

export const customStore = <T>() => {
    const store = writable<{ [key: string]: T }>({})
    const { subscribe, set, update } = store
    return {
        subscribe,
        set,
        update: (key: string, value: T) => {
            update((data) => {
                data[key] = value
                return data
            })
        },
        del: (key: string) => {
            const { [key]: group, ...userWithoutKey } = get(store)
            store.set(userWithoutKey)
        },
    }
}

export const customStoreForArray = <T>() => {
    const store = writable<{ [key: string]: T[] }>({})
    const { subscribe, set, update } = store
    return {
        subscribe,
        set,
        update: (key: string, value: T, uniq: string = '') => {
            update((data) => {
                const oldValue = data[key] ?? []
                let newValue = [...oldValue, value]
                if (uniq) {
                    newValue = uniqBy(newValue, uniq)
                }
                data[key] = newValue
                return data
            })
        },
        del: (key: string) => {
            const { [key]: group, ...userWithoutKey } = get(store)
            store.set(userWithoutKey)
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
