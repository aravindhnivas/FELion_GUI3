import { writable } from 'svelte/store'

function openModalStore() {
    const defaultValues = {
        modalTitle: 'Title',
        type: 'warning',
        modalContent: 'Content',
        open: false,
        message: 'Pre-message',
    }

    const { subscribe, set, update } = writable(defaultValues)

    return {
        subscribe,
        set,
        update,
        error(
            modalContent = '',
            modalTitle = 'Error Details',
            type = 'danger',
            message = 'Error Ocurred'
        ) {
            update((n) => {
                return { modalTitle, type, modalContent, message, open: true }
            })
        },
        info(
            modalContent = '',
            modalTitle = 'Output',
            type = 'warning',
            message = 'Output'
        ) {
            update((n) => {
                return { modalTitle, type, modalContent, message, open: true }
            })
        },
        reset: () => set(defaultValues),
    }
}

const makeStore = (initial) => {

    const { subscribe, set, update } = writable(initial)
    return {
        subscribe,
        set,
        update,
        reset: () => set(initial),
        show: (value) => {
            update((n) => {
                return { ...n, ...value, open: true }
            })
        }
    }

}

export const mainPreModal = openModalStore()
export const activePage = writable('')
export const running_processes = writable([])
export const updateInterval = writable(db.get('updateInterval'))

export const confirmbox = makeStore({title: 'Confirm', content: '', open: false, response: 'Cancel', callback: () => {}})
if (!db.has('updateInterval')) {
    db.set('updateInterval', 15)
}
