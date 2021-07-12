
export const findAndGetValue = (arr, label) => {
    const {value} = _.find(arr, (f)=>f.label==label)
    return value
}