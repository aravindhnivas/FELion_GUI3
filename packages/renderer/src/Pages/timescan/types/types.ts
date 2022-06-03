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