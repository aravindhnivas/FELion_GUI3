export type dataType = { x: number[], y: number[], error_y: { array: number[] } } ;
export interface mainDataType {
    SUM: dataType;
    [mass: string]: dataType;
}

export type totalMassKeyType = {
    mass: string
    id: string
    included: boolean
}[]


export type loss_channelsType = {
    type: string
    name: string
    lossFrom: string
    attachTo: string
    id: string
    numberDensity?: string
}