import { writeFile } from 'fs/promises'
import { execSync } from 'child_process'
import electron from 'electron'
import path from 'path'

function getVendors(): NodeJS.ProcessVersions {
    const output = execSync(`${electron} -p "JSON.stringify(process.versions)"`, {
        env: { ELECTRON_RUN_AS_NODE: '1' },
        encoding: 'utf-8',
    })
    return JSON.parse(output)
}

function updateVendors() {
    const electronRelease = getVendors()
    const nodeMajorVersion = electronRelease.node.split('.')[0]
    const chromeMajorVersion = electronRelease.v8.split('.')[0] + electronRelease.v8.split('.')[1]
    const browserslistrcPath = path.resolve(process.cwd(), '.browserslistrc')

    return Promise.all([
        writeFile(
            './.electron-vendors.cache.json',
            JSON.stringify(
                {
                    chrome: chromeMajorVersion,
                    node: nodeMajorVersion,
                },
                null,
                2
            ) + '\n'
        ),
        writeFile(browserslistrcPath, `Chrome ${chromeMajorVersion}\n`, 'utf8'),
    ])
}

updateVendors().catch((err) => {
    console.error(err)
    process.exit(1)
})
