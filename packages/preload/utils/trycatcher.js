export function syncTryCatcher(fn) {
    let output, error
    return function () {
        try {
            output = fn.apply(this, arguments)
        } catch (err) {
            error = err
            // console.error(err?.stack || err)
        }
        return [output, error]
    }
}

export function asyncTryCatcher(fn) {
    let output, error
    return async function () {
        try {
            output = await fn.apply(this, arguments)
        } catch (err) {
            error = err
            // console.error(err?.stack || err)
        }
        return [output, error]
    }
}
