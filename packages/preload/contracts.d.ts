/* eslint-disable @typescript-eslint/consistent-type-imports */
interface Exposed {
    readonly fs: Readonly<typeof import('./fs-modules').fsUtils>;
    readonly path: Readonly<typeof import('./path-modules').path>;
    readonly db: Readonly<typeof import('./jsondb-modules').dbObject>;

    readonly stopServer: typeof import('./mangeServer').stopServer;
    readonly startServer: typeof import('./mangeServer').startServer;

    readonly execSync: typeof import('./child-process-modules').execSync;
    readonly spawn: typeof import('./child-process-modules').spawnFn;
    readonly exec: Readonly<typeof import('./child-process-modules').computeExecCommand>;

    readonly dialogs: Readonly<typeof import('./dialogs-modules').dialogs>;
    readonly reload: Readonly<typeof import('./dialogs-modules').reload>;
    readonly relaunch: Readonly<typeof import('./dialogs-modules').relaunch>;
    readonly appInfo: Readonly<typeof import('./definedENV').appInfo>;
    readonly __dirname: Readonly<typeof import('./definedENV').__dirname>;
    readonly ROOT_DIR: Readonly<typeof import('./definedENV').ROOT_DIR>;
    readonly appVersion: Readonly<typeof import('./definedENV').appVersion>;

}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface Window extends Exposed {}
