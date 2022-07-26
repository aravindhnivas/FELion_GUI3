import type { SvelteToastOptions } from '@zerodevx/svelte-toast'

export {};

declare global {

    type ButtonClickEvent = MouseEvent | MouseEvent & {
        currentTarget: EventTarget & HTMLButtonElement
    }

    interface Exposed {
        createToast: (description: string, type?: 'info' | 'danger' | 'warning' | 'success', opts?: SvelteToastOptions) => void;

        sleep: (ms: number) => Promise<void>;
        handleError: (error: Error | string) => void;
        getID: () => string;
        clickOutside: (node: HTMLElement) => { destroy: () => void };
    
    }

    interface Window extends Exposed {}

}
