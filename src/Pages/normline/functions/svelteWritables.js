import { writable } from 'svelte/store';

export const felixIndex = writable([])
export const felixPeakTable = writable([])
export const felixOutputName = writable("")
export const opoMode = writable(false)
export const Ngauss_sigma = writable(5)


export const dataTable = writable([])
export const dataTable_avg = writable([])
export const normMethodDatas = writable({})