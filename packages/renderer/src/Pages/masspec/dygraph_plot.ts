import Dygraph, { dygraphs } from 'dygraphs'

export const plotDygraph = (graphDiv: string, data: dygraphs.Data) => {
    const opts: dygraphs.Options = {
        
        labels: ['m/z', 'file1', 'file2'],
        xlabel: 'm/z',
        ylabel: 'Counts',
        title: 'Masspectrum',
        yLabelWidth: 25,
        xLabelHeight: 25,
        titleHeight: 30,

        logscale: true,
        // width: 1000,
        height: 400,
        legend: 'always',
        labelsSeparateLines: true,
        animatedZooms: true,
        labelsDiv: `${graphDiv}-legend`,
        colors: ['#0000FF', '#FF0000'],
        showRoller: true,
        // highlightSeriesOpts: {
        //     strokeWidth: 3,
        //     strokeBorderWidth: 1,
        //     highlightCircleSize: 5
        // },
        // highlightCircleSize: 2,
        // strokeWidth: 1,
        stepPlot: true,
        showRangeSelector: true,
        rangeSelectorHeight: 50,
        // interactionModel: {
        //     'click': function (e, g, context) {
        //         console.log(e, g, context)
        //     },
        //     'dblclick': function (event, g, context) {
        //         if (event.altKey) {
        //             g.resetZoom();
        //         }
        //     }
        // }
    }
    
    const graph = new Dygraph(document.getElementById(graphDiv), data, opts)
    // const graph = new Dygraph(document.getElementById(graphDiv), data)
    graph.ready(() => {
        console.log('graph ready')
        // console.log(graph.getOption('interactionModel'))
    })

    function onclick(event: MouseEvent, xval, points): void {
        
        console.log(event, xval, points);
        if(event.ctrlKey && graph.isZoomed()) {
            graph.resetZoom()
        }
        if (graph.isSeriesLocked()) {
            graph.clearSelection();
        } else {
            graph.setSelection(graph.getSelection(), graph.getHighlightSeries(), true);
        }
    }
    graph.updateOptions({clickCallback: onclick}, true);

    return graph
}