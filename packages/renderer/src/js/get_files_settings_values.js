
const validate_line = (line) => {
    const valid =
        line.trim().length > 0 && line.startsWith('# Sect01 Ion Source')
    return valid
}

export default function(loadfile) {
    return new Promise(async (resolve, reject) => {
        if (!fs.isfile(loadfile)) return reject('Invalid file')

        // const loadfile = pathJoin(location, filename)

        if (!fs.existsSync(loadfile))
            return reject(`${loadfile} does not exist`)

        const [fileContents, error] = await fs.readFile(loadfile)
        if (error) return reject(error)

        const variableValues = {}
        for (const line of fileContents.split('\n')) {
            if (!validate_line(line)) continue
            const keyValuesLine = line.split(' ')
            const key = keyValuesLine[7]
            const value = parseFloat(keyValuesLine[9])
            variableValues[key] = value
        }
        return resolve(variableValues)
    })
}
