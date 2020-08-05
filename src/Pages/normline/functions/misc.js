
// Importing modules

import {felixopoLocation, felixPeakTable, felixIndex, felixOutputName, felixPlotAnnotations, opoMode, Ngauss_sigma, get} from "./svelteWritables";

export function savefile({file={}, name=""}={}) {

    let filename = path.join(get(felixopoLocation), `${name}.json`)
    fs.writeFile(filename, JSON.stringify({file}), 'utf8', function (err) {

        if (err) {
            console.log("An error occured while writing to File.");
            return window.createToast("An error occured while writing to File.", "danger")
        }
        return window.createToast(`${name}.json has been saved.`, "success");
    });
}

export function loadfile({name=""}={}) {
    let filename = path.join(get(felixopoLocation), `${name}.json`)
    if(!fs.existsSync(filename)) {return window.createToast(`${name}.json doesn't exist in DATA dir.`, "danger")}

    let loadedfile = JSON.parse(fs.readFileSync(filename)).file

    window.createToast(`${name}.json has been loaded.`, "success")
    return loadedfile
}

export function plotlySelection({graphDiv="avgplot", mode="felix"}={}) {

    const avgplot = document.getElementById(graphDiv);

    console.log("Creating plotly selection events for, ", avgplot)

    avgplot.on("plotly_selected", (data) => {

       try {
            console.log(data)
            mode === "felix" ? opoMode.set(false) : opoMode.set(true)


            const { range } = data

            felixIndex.set(range.x)


            const output_name = data.points[0].data.name.split(".")[0]
            felixOutputName.set(output_name)
            console.log(`Selected file: ${get(felixOutputName)}`)

        } catch (error) { console.log("No data available to fit") }

    })
}


export function plotlyClick({graphDiv="avgplot", mode="felix"}={}){

    const avgplot = document.getElementById(graphDiv);
    console.log("Creating plotly click events for, ", avgplot)

    avgplot.on('plotly_click', (data)=>{
    
        console.log("Graph clicked: ", data)

        if (data.event.ctrlKey) {

            console.log("Data point length: ", data.points.length)


            for(let i=0; i<data.points.length; i++){

                console.log("Running cycle: ", i)

                let d = data.points[i]

                let name = d.data.name
                mode === "felix" ? opoMode.set(false) : opoMode.set(true)

                let output_name = get(felixOutputName);

                if (name.includes(output_name)){

                    console.log("Filename: ", output_name)

                    let line_color = d.data.line.color
                    console.log(name)
                    console.log(d, d.x, d.y)

                    let [freq, amp] = [parseFloat(d.x.toFixed(2)), parseFloat(d.y.toFixed(2))]
                    const annotation = { text: `(${freq}, ${amp})`, x: freq, y: amp, font:{color:line_color}, arrowcolor:line_color }
                    felixPlotAnnotations.update(annotate => _.uniqBy([...annotate, annotation], 'text'))
                    Plotly.relayout(graphDiv,{annotations: get(felixPlotAnnotations)})

                    felixPeakTable.update(table => [...table, {freq, amp, sig:get(Ngauss_sigma), id:getID()}])
                    felixPeakTable.update(table => _.uniqBy(table, 'freq'))
                }
            }

            console.log("Running cycle ended")
        } 
    })

}