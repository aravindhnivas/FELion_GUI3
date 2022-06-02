/* eslint-disable @typescript-eslint/consistent-type-imports */
interface Exposed {
    readonly fs: Readonly<typeof import('./fs-modules').fsUtils>;
    readonly path: Readonly<typeof import('./path-modules').path>;
    readonly db: Readonly<typeof import('./jsondb-modules').dbObject>;

    readonly stopServer: Readonly<typeof import('./mangeServer').stopServer>;
    readonly startServer: Readonly<typeof import('./mangeServer').startServer>;

    readonly execSync: Readonly<typeof import('./child-process-modules').execSync>;
    readonly spawn: Readonly<typeof import('./child-process-modules').spawnFn>;
    readonly exec: Readonly<typeof import('./child-process-modules').computeExecCommand>;

    readonly dialogs: Readonly<typeof import('./dialogs-modules').dialogs>;
    readonly reload: Readonly<typeof import('./dialogs-modules').reload>;
    readonly relaunch: Readonly<typeof import('./dialogs-modules').relaunch>;

}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface Window extends Exposed {}
