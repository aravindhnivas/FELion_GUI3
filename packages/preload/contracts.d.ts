/* eslint-disable @typescript-eslint/consistent-type-imports */

interface Exposed {
    readonly fs: Readonly<typeof import('./fs-modules').fsUtils>;
    readonly path: Readonly<typeof import('./path-modules').path>;
}


// eslint-disable-next-line @typescript-eslint/no-empty-interface
interface Window extends Exposed {}