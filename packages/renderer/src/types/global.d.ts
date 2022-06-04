
export {};
declare global {
    interface ButtonClickEvent extends PointerEvent {
        readonly target: HTMLButtonElement;
    }
}