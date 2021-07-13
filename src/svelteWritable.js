
import { writable } from 'svelte/store';
export const mainPreModal = writable({
    modalTitle:"Error Details",
    type:"danger",
    message:"Error Occured",
    forError(){
        this.modalTitle = "Error Details"
        this.type = "danger"
        this.message = "Error Occured"
    },
    forInfo() {

        this.modalTitle = "Output result"
        this.type = "info"
        this.message = "Output"
    
    }


})