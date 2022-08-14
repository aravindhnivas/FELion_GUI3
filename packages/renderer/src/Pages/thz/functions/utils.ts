export const save_data_to_file = async (filename: string, data: string) => {
    window.fs.ensureDirSync(window.path.dirname(filename))
    const output = await window.fs.writeFile(filename, data)
    const saveInfo = {msg: '', error: ''}
    if (window.fs.isError(output)) {
        saveInfo.error = output.message
        return Promise.resolve(saveInfo)
    }
    saveInfo.msg = `Saved to ${filename}`
    window.createToast(`Data saved`)
    return Promise.resolve(saveInfo)
}

export function makeTableRow(coefficient: ValueLabel, rateMultiplier: string | null = null) {
    const { label, value } = coefficient
    const levelLabels = label.split(' --> ').map((f) => f.trim())
    const tableRow = `${levelLabels[1]} & $\\rightarrow$ & ${levelLabels[0]} & ${formatNumber(value)}`
    if (rateMultiplier === null)
        return `${tableRow} \\\\`

    const Rate = Number(value) * Number(rateMultiplier)
    const RateValue = formatNumber(Rate.toExponential(1))
    return `${tableRow} & ${RateValue} \\\\`
}

export function formatNumber(value: string | number, dec:number=1, fmt: string = '\\cdot') {
    // if (value === undefined) return ''
    const numbers = Number(value).toExponential(dec).split('e')
    return `$${numbers[0]} ${fmt} 10^{${numbers[1].replace('+', '')}}$`
}

export function makeTable(caption: string, label: string, column_align:string, header: string, body: string) {
    let fullTable = ''
    fullTable += `\\begin{table}`
    fullTable += `\n\t\\centering`
    fullTable += `\n\t\\caption{${caption}}`
    fullTable += `\n\t\\label{${label}}`
    fullTable += `\n\t\\begin{tabular}{${column_align}}`
    fullTable += `\n\t\t\\hline`
    fullTable += `\n\t\t${header} \\\\`
    fullTable += `\n\t\t\\hline\\hline\\\\`
    fullTable += `\n\t\t${body}`
    fullTable += `\n\t\t\\hline\\hline\\\\`
    fullTable += `\n\t\\end{tabular}`
    fullTable += `\n\\end{table}`
    console.log(fullTable)
    return fullTable
}
