export function init_tour_normline({filetype="felix"}={}) {
        
    const intro = introJs()
    intro.setOptions({

        steps: [

            {
                element: document.getElementById(`${filetype}_filebrowser_btn`),
                intro: "Browse file location folder"
            },
            {
                element: document.getElementById(`${filetype}_filebrowser`),
                intro: "Select file(s) here", position:"right"
            },
            {
                element: document.getElementById('create_baseline_btn'),
                intro: "Create/ajusting baseline"
            },
            {
                element: document.getElementById('felix_plotting_btn'),
                intro: "After creating baseline -> Plot the graph (NOTE: .pow file should be already present in DATA folder)"
            },

        ], showProgress: true, showBullets:false
      
    })

    console.log("Starting introduction tour");
    intro.start()

    intro.onbeforeexit(function() {
        console.log("introduction tour exited");

        // return false; // returning false means don't exit the intro
    
    });

    intro.onbeforechange(function(targetElement) {
        console.log("before new step",targetElement);
    });

    intro.onafterchange(function(targetElement) {
        console.log("after new step",targetElement);
    });

    intro.oncomplete(function() {
        console.log("introduction tour completed");
    });
}