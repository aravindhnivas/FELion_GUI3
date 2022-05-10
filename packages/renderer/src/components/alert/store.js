import { writable } from 'svelte/store'
const makeStore = (initial = {}) => {
    const { subscribe, set, update } = writable(initial)
    return {
        subscribe,
        set,
        update,
        reset: () => set(initial),
        push(obj) {
            update((n) => {
                return { ...n, ...obj, open: true }
            })
        },
    }
}
export const showConfirm = makeStore({
    open: false,
    title: 'Confirm',
    content: 'Are you sure?',
    callback: null,
})