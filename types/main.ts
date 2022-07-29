export const appPathKeys = <const>[
    'appData',
    'userData',
    'cache',
    'temp',
    'exe',
    'module',
    'logs',
    'crashDumps',
]
export type AppInfo = Record<typeof appPathKeys[number] | 'ROOT_DIR' | 'appPath' | 'resource_directory', string>
