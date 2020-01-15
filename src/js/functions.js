
window.showpage = (item) => {document.getElementById(item).style.display = "block"; console.log(`Opened: ${item}`)}
window.hidepage = (item) => {document.getElementById(item).style.display = "none"; console.log(`Closed: ${item}`)}