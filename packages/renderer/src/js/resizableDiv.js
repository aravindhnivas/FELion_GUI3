
import interact from 'interactjs'

export function resizableDiv({ 
    div, 
    change = { width: true, height: true }, 
    edges = { left: false, right: false, bottom: false, top: false }
    } = {}) {
    
        document.querySelector(div)?.style.setProperty("touch-action", "none")

    interact(div).resizable({
        edges,
        modifiers: [
            // keep the edges inside the parent

            interact.modifiers.restrictEdges({ outer: 'parent' }),
            interact.modifiers.restrictSize({ min: { width: 50, height: 50 }, max: { width: 500 } })
        ],
        inertia: true



    }).on('resizemove', function (event) {
        let target = event.target
        let x = (parseFloat(target.getAttribute('data-x')) || 0)
        let y = (parseFloat(target.getAttribute('data-y')) || 0)
        if (change.width) {
            target.style.width = event.rect.width + 'px'
            if (event.rect.width <= 50) {
                if (target.classList.contains("filebrowser")) { target.style.display = "none" }
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
}
resizableDiv({ div: ".left_container__div", edges: { right: true }, change: { width: true, height: false } })