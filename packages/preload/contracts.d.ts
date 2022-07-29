/* eslint-disable @typescript-eslint/consistent-type-imports */
interface Exposed {
    readonly fs: Readonly<typeof import('./fs-modules').fsUtils>;
    readonly path: Readonly<typeof import('./path-modules').path>;
    readonly db: Readonly<typeof import('./jsondb-modules').dbObject>;
    readonly persistentDB: typeof import('./persistentDB').persistentDB;
    readonly stopServer: typeof import('./mangeServer').stopServer;
    readonly startServer: typeof import('./mangeServer').startServer;

    readonly execSync: typeof import('./child-process-modules').execSync;
    readonly spawn: typeof import('./child-process-modules').spawnFn;
    readonly exec: typeof import('./child-process-modules').exec;

    readonly dialogs: Readonly<typeof import('./dialogs-modules').dialogs>;
    readonly reload: Readonly<typeof import('./dialogs-modules').reload>;
    readonly relaunch: Readonly<typeof import('./dialogs-modules').relaunch>;
    appInfo: typeof import('./definedEnv').appInfo;
    readonly ROOT_DIR: Readonly<typeof import('./definedEnv').ROOT_DIR>;
    readonly appVersion: Readonly<typeof import('./definedEnv').appVersion>;
    readonly platform: Readonly<typeof import('./definedEnv').platform>;
    readonly versions: Readonly<typeof import('./definedEnv').versions>;
    readonly isPackaged: Readonly<typeof import('./definedEnv').isPackaged>;
    readonly shell: Readonly<typeof import('./definedEnv').shellUtils>;
    readonly checkupdate: typeof import('./update-log').checkupdate;
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface Window extends Exposed {}
