export function get_details_func(dataFromPython) {
    let filedetails = [];
    dataFromPython.files.forEach(data=>{
        let {filename, trap, res, b0, range} = data
        let [min, max] = range
        filedetails = [...filedetails, {filename, min, max, trap, b0, res, precursor:"", ie:"", temp:"", id:getID()}]
    })

    return filedetails;

}