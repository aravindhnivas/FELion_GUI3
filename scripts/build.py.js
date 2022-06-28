const {spawn} = require('child_process')

function build() {
    const args = "run -n felionpy pyinstaller D:\\FELion_GUI3\\resources\\build\\felionpy.spec --distpath D:\\FELion_GUI3\\resources --workpath D:\\FELion_GUI3\\resources\\build --noconfirm".split(' ')
    console.log({ args })
    const child = spawn('conda', args, { shell: true })
    child.stdout.on('data', (data) => { console.log(data.toString()) })
    child.stderr.on('data', (data) => { console.log(data.toString()) })
    child.on('close', (code) => { console.log(`child process exited with code ${code}`) })
}
build()