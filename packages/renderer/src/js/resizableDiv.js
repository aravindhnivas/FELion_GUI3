import interact from 'interactjs'

const dispatchInteractEvent = (element, eventName, detail) => {
    const event = new CustomEvent(eventName, {
        bubbles: false,
        cancelable: true,
        detail,
    })

    element.dispatchEvent(event)
}

// Draggable: dragstart, dragmove, draginertiastart, dragend
// Resizable: resizestart, resizemove, resizeinertiastart, resizeend
// Gesturable: gesturestart, gesturemove, gestureend

export function resizableDiv(
    target,
    // width=true, height=true,
    // left=true, top=false,
    // right=false, bottom=false,
    // change = { width: true, height: false },
    // edges = { left: false, right: true, bottom: false, top: false }
    params = {
        change: { width: true, height: false },
        edges: { left: false, right: true, bottom: false, top: false },
    }
) {
    // const change = { width, height }
    // const edges = { left, right, bottom, top }
    const { change, edges } = params
    console.log('resizableDiv', target, params)
    interact(target)
        .resizable({
            edges,
            modifiers: [
                // keep the edges inside the parent

                interact.modifiers.restrictEdges({ outer: 'parent' }),
                interact.modifiers.restrictSize({
                    min: { width: 50, height: 50 },
                    max: { width: 500, height: 500 },
                }),
            ],
            inertia: true,
        })
        .on('resizemove', function (event) {
            const target = event.target
            dispatchInteractEvent(target, 'resizemove', event)
            let x = parseFloat(target.getAttribute('data-x')) || 0
            let y = parseFloat(target.getAttribute('data-y')) || 0
            if (change.width) {
                target.style.width = event.rect.width + 'px'
                if (event.rect.width <= 50) {
                    if (target.classList.contains('filebrowser')) {
                        target.style.display = 'none'
                    }
                }
            }
            if (change.height) target.style.height = event.rect.height + 'px'
            // translate when resizing from top or left edges
            x += event.deltaRect.left
            y += event.deltaRect.top
            target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)'
            target.setAttribute('data-x', x)
            target.setAttribute('data-y', y)
        })
        .on('resizeend', function (event) {
            dispatchInteractEvent(event.target, 'resizeend', event)
        })
        .on('resizestart', function (event) {
            dispatchInteractEvent(event.target, 'resizestart', event)
        })
}
