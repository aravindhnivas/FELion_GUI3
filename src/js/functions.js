window.showpage = (item) => {document.getElementById(item).style.display = "block"; console.log(`Opened: ${item}`)}
window.hidepage = (item) => {document.getElementById(item).style.display = "none"; console.log(`Closed: ${item}`)}
window.togglepage = (item) => {
    let element = document.getElementById(item);
    let display = element.style.display;
    display == "none" ? element.style.display = "block" : element.style.display = "none"
}

export function resizableDiv({div, change={width:true, height:true} ,cursor={left:false, right:false, bottom:false, top:false}}={}) {
    interact(div).resizable({
        edges: cursor,
        modifiers: [

            // keep the edges inside the parent
            interact.modifiers.restrictEdges({outer: 'parent'}),
            interact.modifiers.restrictSize({min: { width: 300, height: 50 }, max: { width: 500 }})
        ],
        inertia: true
    }).on('resizemove', function (event) {
        let target = event.target
        let x = (parseFloat(target.getAttribute('data-x')) || 0)
        let y = (parseFloat(target.getAttribute('data-y')) || 0)

        if (change.width) target.style.width = event.rect.width + 'px'
        if (change.height) target.style.height = event.rect.height + 'px'

        // translate when resizing from top or left edges
        x += event.deltaRect.left
        y += event.deltaRect.top

        target.style.webkitTransform = target.style.transform = 'translate(' + x + 'px,' + y + 'px)'
        target.setAttribute('data-x', x)
        target.setAttribute('data-y', y)
    })    

}

let resizeBrowser = resizableDiv({div:".filebrowser", cursor:{right:true}, change:{width:true, height:false}})

console.log(resizeBrowser)