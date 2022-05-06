export function syncTryCatcher(fn) {
    return function () {
        try {
            const output = fn.apply(this, arguments)
            return [output, null]
        } catch (err) {
            const error = err
            return [null, error]
        }
    }
}

export function asyncTryCatcher(fn) {
    return async function () {
        try {
            const output = await fn.apply(this, arguments)
            return [output, null]
        } catch (err) {
            const error = err
            return [null, error]
        }
    }
}
