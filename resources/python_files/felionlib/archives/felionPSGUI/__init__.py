from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.figure import Figure
import matplotlib
matplotlib.use("TkAgg")
import PySimpleGUI as sg

def draw_figure_w_toolbar(
    canvasFrame, fig: Figure, toolbarFrame
) -> FigureCanvasTkAgg:

    if canvasFrame.children:
        for child in canvasFrame.winfo_children():
            child.destroy()

    if toolbarFrame.children:
        for child in toolbarFrame.winfo_children():
            child.destroy()

    canvas = FigureCanvasTkAgg(fig, master=canvasFrame)
    canvas.draw()

    toolbar = Toolbar(canvas, toolbarFrame)
    toolbar.update()

    canvas.get_tk_widget().pack(side='right', fill='both', expand=1)

    return canvas


class Toolbar(NavigationToolbar2Tk):
    def __init__(self, *args, **kwargs):
        super(Toolbar, self).__init__(*args, **kwargs)


class felionPSGUI:
    def __init__(
        self,
        layout,
        # canvasKey,
        title="felionPSGUI-figure",
        finalize=True,
        *args,
        **kwargs
    ):

        # create the form and show it without the plot
        self.window = sg.Window(title, layout, finalize=finalize, *args, **kwargs)
        self.layout = layout

    def initFigure(self, canvasFrameKey, toolbarFrameKey, *args, **kwargs):

        self.fig = Figure(*args, **kwargs)
        canvasFrame = self.window[canvasFrameKey].TKCanvas
        toolbarFrame = self.window[toolbarFrameKey].TKCanvas

        self.canvas = draw_figure_w_toolbar(canvasFrame, self.fig, toolbarFrame)
    
    def updatefigure(self):
        width, height = self.window.size
        DPI = self.fig.dpi
        self.fig.set_size_inches(width/DPI, height/DPI)
        self.fig.tight_layout()
        self.canvas.draw_idle()

def makeLayout(canvasFrameKey, toolbarFrameKey):

    layout = [
        [sg.Canvas(key=toolbarFrameKey)],
        [sg.Column(
            layout=[
                [
                    sg.Canvas(
                        key=canvasFrameKey,
                        # it's important that you set this size
                        # size=(400 * 2, 400)
                    )
                ]
            ],
            background_color='#FFF',
            pad=(0, 0)
        )],
        [sg.B('Alive?')]

    ]

    return layout


def main():
    canvasFrameKey = '-CANVAS-'
    toolbarFrameKey = '-TOOLBAR-'

    layout = makeLayout(canvasFrameKey, toolbarFrameKey)

    widget = felionPSGUI(layout, resizable=True)
    
    widget.window.bind('<Configure>', "RESIZE")
    widget.initFigure(canvasFrameKey, toolbarFrameKey)

    widget.ax = widget.fig.add_subplot(111)
    widget.ax.plot([1, 2, 3], [1, 2, 3])
    widget.updatefigure()

    # Create an event loop
    while True:
        
        event, values = widget.window.read()
        print(event, values)
        
        if event in (sg.WIN_CLOSED, 'Exit'):  # always,  always give a way out!
            break
        
        elif event == "RESIZE":
            figDPI = widget.fig.dpi
            width, height = widget.window.size
            widget.updatefigure()
            print(width, height, figDPI)
            print("fig:updated")
            

    widget.window.close()
