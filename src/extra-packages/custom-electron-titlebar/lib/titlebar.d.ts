import { Color } from './common/color';
import { MenubarOptions } from './menubar';
import { Theme, Themebar } from './themebar';
export interface TitlebarOptions extends MenubarOptions {
    /**
     * The background color of the titlebar.
     */
    backgroundColor: Color;
    /**
     * The icon shown on the left side of the title bar.
     */
    icon?: string;
    /**
     * Style of the icons.
     * You can create your custom style using [`Theme`](https://github.com/AlexTorresSk/custom-electron-titlebar/THEMES.md)
     */
    iconsTheme?: Theme;
    /**
     * The shadow color of the titlebar.
     */
    shadow?: boolean;
    /**
     * Define if the minimize window button is displayed.
     * *The default is true*
     */
    minimizable?: boolean;
    /**
     * Define if the maximize and restore window buttons are displayed.
     * *The default is true*
     */
    maximizable?: boolean;
    /**
     * Define if the close window button is displayed.
     * *The default is true*
     */
    closeable?: boolean;
    /**
     * Set the order of the elements on the title bar. You can use `inverted`, `first-buttons` or don't add for.
     * *The default is normal*
     */
    order?: "inverted" | "first-buttons";
    /**
     * Set horizontal alignment of the window title.
     * *The default value is center*
     */
    titleHorizontalAlignment?: "left" | "center" | "right";
    /**
     * Sets the value for the overflow of the window.
     * *The default value is auto*
     */
    overflow?: "auto" | "hidden" | "visible";
    /**
     * When the close button is clicked, the window is hidden instead of closed.
     * *The default is false*
     */
    hideWhenClickingClose?: boolean;
}
export declare class Titlebar extends Themebar {
    private titlebar;
    private title;
    private dragRegion;
    private appIcon;
    private menubarContainer;
    private windowControls;
    private maxRestoreControl;
    private container;
    private resizer;
    private isInactive;
    private currentWindow;
    private _options;
    private menubar;
    private events;
    constructor(options?: TitlebarOptions);
    private closeMenu;
    private registerListeners;
    private removeListeners;
    private createTitlebar;
    private onBlur;
    private onFocus;
    private onMenubarVisibilityChanged;
    private onMenubarFocusChanged;
    private onDidChangeWindowFocus;
    private onDidChangeMaximized;
    private onDidChangeFullscreen;
    private updateStyles;
    /**
     * get the options of the titlebar
     */
    get options(): TitlebarOptions;
    /**
   * Update the background color of the title bar
   * @param backgroundColor The color for the background
   */
    updateBackground(backgroundColor: Color): void;
    /**
   * Update the title of the title bar.
   * You can use this method if change the content of `<title>` tag on your html.
   * @param title The title of the title bar and document.
   */
    updateTitle(title?: string): void;
    /**
     * It method set new icon to title-bar-icon of title-bar.
     * @param path path to icon
     */
    updateIcon(path: string): void;
    /**
     * Update the default menu or set a new menu.
     * @param menu The menu.
     */
    updateMenu(menu: Electron.Menu): void;
    /**
     * Update the position of menubar.
     * @param menuPosition The position of the menu `left` or `bottom`.
     */
    updateMenuPosition(menuPosition: "left" | "bottom"): void;
    /**
     * Horizontal alignment of the title.
     * @param side `left`, `center` or `right`.
     */
    setHorizontalAlignment(side: "left" | "center" | "right"): void;
    /**
     * Remove the titlebar, menubar and all methods.
     */
    dispose(): void;
}
