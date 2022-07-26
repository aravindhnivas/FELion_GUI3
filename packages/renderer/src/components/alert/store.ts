import { writable } from 'svelte/store'
const makeStore = <T>(initial: T) => {
    const { subscribe, set, update } = writable(initial)
    return {
        subscribe,
        set,
        update,
        reset: () => set(initial),
        push(obj: T) {
            update((n: T) => {
                return { ...n, ...obj, open: true }
            })
        },
    }
}

const defaultAlert = {
    open: false,
    title: 'Confirm',
    content: 'Are you sure?',
    callback: (response: string): void => {},
}
export const showConfirm = makeStore(defaultAlert)
