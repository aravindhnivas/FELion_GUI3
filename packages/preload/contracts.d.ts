/* eslint-disable @typescript-eslint/consistent-type-imports */

interface Exposed {
    readonly fs: Readonly<typeof import('./fs-modules').fsUtils>;
    // readonly versions: Readonly<typeof import('./src/versions').versions>;
}


// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface Window extends Exposed {}