import get_files_settings_values from '$src/js/get_files_settings_values'

export async function readMassFile(massfiles) {
    const loadbtn = document.getElementById('masspec-plot-btn')
    if (loadbtn.classList.contains('is-loading')) {
        const warnmsg = 'Wait untill the previous file(s) are plotted'
        window.createToast(warnmsg, 'warning')
        return [null, warnmsg]
    }

    loadbtn.classList.toggle('is-loading')

    try {
        const dataToSend = {}

        for (const filename of massfiles) {
            if (!fs.existsSync(filename)) return
            const [fileContents] = await fs.readFile(filename)

            const name = basename(filename)
            console.info('content read: ', name)
            const dataContents = fileContents
                .split('\n')
                .filter((line) => !line.includes('#'))
                .map((line) =>
                    line
                        .trim()
                        .split('\t')
                        .map((data) => parseFloat(data))
                )

            console.info(name, 'filtered')
            const [x, y] = dataContents[0].map((_, colIndex) =>
                dataContents.map((row) => row[colIndex])
            )
            const mode = 'lines'
            const showlegend = true
            console.info(name, 'done\n')

            const fileVariableComputedValues = await get_files_settings_values(
                filename
            )
            const res = fileVariableComputedValues['m03_ao13_reso']
            const b0 = fileVariableComputedValues['m03_ao09_width'] / 1000
            const trap = fileVariableComputedValues['m04_ao04_sa_delay'] / 1000

            const label = `${name}: Res:${res?.toFixed(1)} V; B0: ${b0?.toFixed(
                0
            )} ms; trap: ${trap?.toFixed(0)} ms`
            dataToSend[name] = { x, y, name: label, mode, showlegend }
        }

        console.info('File read completed')
        console.info(dataToSend)
        return [dataToSend, null]
    } catch (error) {
        window.handleError(error)
        return [null, error]
    } finally {
        loadbtn.classList.toggle('is-loading')
    }
}
