from matplotlib.widgets import Button, TextBox, CheckButtons
from .savedata import saveData

widget = None
numberDensity = None
# numberDensityWidget, saveButton, checkbox, button = [None]*4
checkboxes = {
    "setbound": False
}


def checkboxesFunc(label):
    global checkboxes
    checkboxes[label] = not checkboxes[label]
    widget.canvas.draw_idle()


def setNumberDensity(val):
    global numberDensity
    numberDensity = float(val)
    print(f"{numberDensity=}", flush=True)
    # widget.ax.set_title(f"{selectedFile}: {temp:.1f} K {numberDensity:.2e}"+"$cm^{-3}$")

    fitfunc()


def make_widgets(**kwargs):

    global widget, fitfunc, numberDensity
    # global numberDensityWidget, saveButton, checkbox, button

    widget = kwargs["widget"]
    fitfunc = kwargs["fitfunc"]
    numberDensity = kwargs["numberDensity"]

    left, bottom, width, height = 0.1, 0.05, 0.1, 0.05

    axcolor = 'lightgoldenrodyellow'

    buttonAxes = widget.fig.add_axes(
        [left, bottom, width, height],
        facecolor=axcolor
    )

    button = Button(buttonAxes, 'Fit', color=axcolor, hovercolor='0.975')
    button.on_clicked(fitfunc)

    left += width+0.01
    checkAxes = widget.fig.add_axes(
        [left, bottom, width, height],
        facecolor=axcolor
    )

    checkbox = CheckButtons(checkAxes, ("setbound", ),
                            list(checkboxes.values()))
    checkbox.on_clicked(checkboxesFunc)

    left += width+0.01

    saveButtonAxes = widget.fig.add_axes(
        [left, bottom, width, height],
        facecolor=axcolor
    )

    saveButton = Button(saveButtonAxes, 'saveData',
                        color=axcolor, hovercolor='0.975')
    saveButton.on_clicked(saveData)

    numberDensityWidgetAxes = widget.fig.add_axes(
        [0.9-width, bottom, width, height],
        facecolor=axcolor
    )

    numberDensityWidget = TextBox(
        numberDensityWidgetAxes, 'Number density',
        initial=f"{numberDensity:.2e}"
    )

    numberDensityWidget.on_submit(setNumberDensity)
    widget.bottomWidgets = [
        buttonAxes, checkAxes,
        saveButtonAxes, numberDensityWidgetAxes
    ]
    # return numberDensityWidget, saveButton, checkbox, button
