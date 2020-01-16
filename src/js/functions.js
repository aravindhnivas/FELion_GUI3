
window.showpage = (item) => {document.getElementById(item).style.display = "block"; console.log(`Opened: ${item}`)}
window.hidepage = (item) => {document.getElementById(item).style.display = "none"; console.log(`Closed: ${item}`)}
window.togglepage = (item) => {
    let element = document.getElementById(item);
    let display = element.style.display;
    display == "none" ? element.style.display = "block" : element.style.display = "none"
    
}