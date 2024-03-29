import type { SvelteToastOptions } from '@zerodevx/svelte-toast'
// export {};

const felix_opo_data_from_python = <const>["SA", "pow", "base", "average", "average_per_photon", "average_rel"];
declare global {
    
    type PlotData = Partial<Plotly.PlotData>
    interface DataFromPython {
        [key: string]: PlotData
    }
    type FELIXData = Record<typeof felix_opo_data_from_python[number], DataFromPython>

    type OPOData = Omit<FELIXData, "SA">

    type ButtonClickEvent = MouseEvent | MouseEvent & {
        currentTarget: EventTarget & HTMLButtonElement
    }

    interface OnlyValueLabel<T=string> {
        value: T
        label: string
    }
    interface ValueLabel<T = string> { 
        value: T; label: string; step?: string, id: string
    }

    type KeyStringObj<T=string> = {[key: string]: T}

    type persistentDB<T> = ReturnType<typeof window.persistentDB<T>>
    
    interface Exposed {
        createToast: typeof import('../src/js/functions').createToast;
        handleError: typeof import('../src/js/functions').handleError;
        sleep: (ms: number) => Promise<void>;
        getID: () => string;
        clickOutside: (node: HTMLElement) => { destroy: () => void };
        error: unknown;
    }
    interface Window extends Exposed {}
}
