
import { writable } from 'svelte/store';

function openModalStore() {

    const defaultValues = { 
        modalTitle: "Title", type: "warning", modalContent: "Content", open: false, message: "Pre-message"
    }

    const { subscribe, set, update } = writable(defaultValues);

    return {
    
        subscribe, set, update,
        error(modalContent = "", modalTitle = "Error Details", type = "danger", message = "Error Ocurred") {
            update(n => { return { modalTitle, type, modalContent, message, open: true } })
        },
        info(modalContent = "", modalTitle = "Output", type = "warning", message = "Output") {
            update(n => { return { modalTitle, type, modalContent, message, open: true } })
        },
        reset: () => set(defaultValues)
    };
}

export const mainPreModal = openModalStore()

export const activePage = writable("")
export const running_processes = writable([])
