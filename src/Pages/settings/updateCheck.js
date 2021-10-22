
export function updateCheck(event){
    const {target} = event
    target.classList.toggle("is-loading")
    if (!navigator.onLine) {if (info) {window.createToast("No Internet Connection!", "warning")}; return}
    // checkupdate()
}