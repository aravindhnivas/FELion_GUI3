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
