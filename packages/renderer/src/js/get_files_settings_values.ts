function validate_line(line: string): boolean {
    const valid = line.trim().length > 0 && line.startsWith('# Sect01 Ion Source')
    return valid
}

export default function (filename: string): Promise<{ [name: string]: number }> {
    return new Promise(async (resolve, reject) => {
        if (!window.fs.isFile(filename)) return reject('Invalid file')
        if (!window.fs.isFile(filename)) return reject(`${filename} does not exist`)

        const fileContents = await window.fs.readFile(filename)
        if (window.fs.isError(fileContents)) return reject(fileContents)

        const variableValues: { [name: string]: number } = {}
        for (const line of fileContents.split('\n')) {
            if (!validate_line(line)) continue
            const keyValuesLine = line.split(' ')
            const key = keyValuesLine[7]
            const value = parseFloat(keyValuesLine[9])
            variableValues[key] = value
        }
        console.log(variableValues)
        return resolve(variableValues)
    })
}
