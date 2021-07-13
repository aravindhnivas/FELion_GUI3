
export const findAndGetValue = (arr, label) => {
    let values=[];
    if (typeof label === "object") {
        label.forEach(l=>{
            const {value} = _.find(arr, (f)=>f.label==l)
            values = [...values, value]

        })
        return values

    } else {

        const {value} = _.find(arr, (f)=>f.label==label)
        return value
    }
    
}