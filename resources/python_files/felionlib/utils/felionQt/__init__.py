import sys
import traceback
from pathlib import Path as pt

from typing import Any, Callable, Iterable, Optional, Union
from PyQt6.QtCore import Qt
import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtGui import QIcon
import matplotlib as mpl
from matplotlib.artist import Artist
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.container import Container

from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import key_press_handler
from matplotlib.text import Text
import matplotlib.ticker as plticker
from .utils.widgets import ShowDialog, iconfile


def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb, limit=5))
    print("error catched!:", flush=True)
    print("error message:\n", tb, flush=True)
    ShowDialog("Error Occured", tb, "critical")


sys.excepthook = excepthook


class felionQtWindow(QtWidgets.QMainWindow):

    def __init__(
        self,
        location: str = "",
        title: str = "felionQt-Figure",
        figTitle: str = "",
        figYlabel: str = "",
        figXlabel: str = "",
        savefilename: str = "",
        makeControlLayout: bool = True,
        defaultEvents: bool = True,
        figDPI: int = 100,
        windowGeometry: tuple[int, int] = (1200, 700),
        includeCloseEvent: bool = False,
        **kwargs: dict[str, Any],
    ) -> None:

        super().__init__()

        self._main = QtWidgets.QWidget()

        self.setCentralWidget(self._main)
        self.setWindowTitle(title)
        self.resize(*windowGeometry)
        self.setWindowIcon(QIcon(iconfile.resolve().__str__()))

        self.location = pt(location).resolve()
        self.savefilename = savefilename
        
        self.figTitle = figTitle
        self.figYlabel = figYlabel
        self.figXlabel = figXlabel

        self.mainLayout = QtWidgets.QHBoxLayout(self._main)

        if includeCloseEvent:
            self.closeEvent = lambda event: closeEvent(self, event)
            
        figureArgs = {"dpi": figDPI}
        if "figureArgs" in kwargs:
            figureArgs = figureArgs | self.kwargs["figureArgs"]
        
        self.init_attributes()

        self.makeFigureLayout(figureArgs=figureArgs, defaultEvents=defaultEvents)
        self.makeControlLayout = makeControlLayout
        if self.makeControlLayout:
            self.createControlLayout(optimize=True)

    def init_attributes(self):
        
        self.titleWidget = QtWidgets.QLineEdit("")
        self.xlabelWidget = QtWidgets.QLineEdit("")
        self.ylabelWidget = QtWidgets.QLineEdit("")

    def showWidget(self):

        self.figure_save_controllers()
        self.controlLayout.addStretch()

        controlGroupBox = QtWidgets.QGroupBox()
        controlGroupBox.setLayout(self.controlLayout)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidget(controlGroupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(250)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        finalControlLayout = QtWidgets.QVBoxLayout()
        finalControlLayout.addWidget(scroll)

        self.mainLayout.addLayout(finalControlLayout, 1)

        self.show()
        self.activateWindow()
        self.raise_()

        self.updateFigsizeDetails()
        self.canvas.setFocus()

    def figure_DPI_controller(self):
        def changefigDPI(updateDPI):
            self.fig.set_dpi(updateDPI)
            self.fig.set_size_inches(
                self.canvas.width() / updateDPI,
                self.canvas.height() / updateDPI,
            )

            self.draw()
            self.updateFigsizeDetails()
        
        dpiwidget = self.createSpinBox(int(self.fig.dpi), prefix="DPI: ", _min=70, _step=5, callback=changefigDPI)
        self.controlLayout.addWidget(dpiwidget)

    def draw(self):
        self.canvas.draw_idle()

    def updatecanvas(self):

        self.fig.tight_layout()
        self.draw()

    def figurelabelsWidgetMaker(self, label: str, fontsz: int, labelType: str):

        widgetGroup = QtWidgets.QHBoxLayout()
        labelwidget = QtWidgets.QLineEdit(str(label))
        

        def update_func():
            if labelType == "title":
                self.ax.set_title(labelwidget.text(), fontsize=fontwidget.value())
            elif labelType == "xlabel":
                self.ax.set_xlabel(labelwidget.text(), fontsize=fontwidget.value())
            elif labelType == "ylabel":
                self.ax.set_ylabel(labelwidget.text(), fontsize=fontwidget.value())
            self.draw()

        labelwidget.textChanged.connect(update_func)
        fontwidget = self.createSpinBox(fontsz, _min=5, _step=1, callback=update_func)
        widgetGroup.addWidget(labelwidget, 4)
        widgetGroup.addWidget(fontwidget, 1)

        setattr(self, f"{labelType}Widget", labelwidget)
        setattr(self, f"{labelType}FontWidget", fontwidget)
        return widgetGroup

    def getaxisUpdateFunction(self):

        self.updatefn = {
            "formatter": {
                "major": {"x": self.ax.xaxis.set_major_formatter, "y": self.ax.yaxis.set_major_formatter},
                "minor": {"x": self.ax.xaxis.set_minor_formatter, "y": self.ax.yaxis.set_minor_formatter},
            },
            "ticklocator": {
                "major": {"x": self.ax.xaxis.set_major_locator, "y": self.ax.yaxis.set_major_locator},
                "minor": {"x": self.ax.xaxis.set_minor_locator, "y": self.ax.yaxis.set_minor_locator},
            },
        }

    def updateTicksAndFormatter(self):

        Nlocator = self.tickLocatorWidget.value()

        if self.axisType == "x" and self.XlogScaleWidget.isChecked():
            locator = plticker.LogLocator(numticks=Nlocator)
        elif self.axisType == "y" and self.YlogScaleWidget.isChecked():
            locator = plticker.LogLocator(numticks=Nlocator)
        else:
            locator = plticker.MaxNLocator(Nlocator)
        self.ticklocatorfn(locator)

        if self.tickType == "major":
            minortickfn = self.updatefn["ticklocator"]["minor"][self.axisType]
            minortickfn(plticker.AutoMinorLocator())

        if self.fomartTickCheck.isChecked():
            fmtString = self.tickFormatterWidget.text()
            self.formatterfn(plticker.StrMethodFormatter(fmtString))
        self.draw()

    def update_tick_params(self, _val=0, ax=None, **kwargs):
        ax = ax or self.ax
        ax.tick_params(
            which="major", width=self.tick_major_width_widget.value(), length=self.tick_major_length_widget.value(), **kwargs
        )
        ax.tick_params(
            which="minor", width=self.tick_minor_width_widget.value(), length=self.tick_minor_length_widget.value(), **kwargs
        )
        self.draw()
    
    def major_minor_ticksize_controllers(self):

        major_tick_controller_layout = QtWidgets.QHBoxLayout()

        self.tick_major_width_widget = self.createSpinBox(2, _min=1, prefix="width: ", callback=self.update_tick_params)
        self.tick_major_length_widget = self.createSpinBox(
            12, _min=1, prefix="length: ", callback=self.update_tick_params
        )
        major_tick_controller_layout.addWidget(QtWidgets.QLabel("major"))

        major_tick_controller_layout.addWidget(self.tick_major_width_widget)
        major_tick_controller_layout.addWidget(self.tick_major_length_widget)

        minor_tick_controller_layout = QtWidgets.QHBoxLayout()

        self.tick_minor_width_widget = self.createSpinBox(1, _min=1, prefix="width: ", callback=self.update_tick_params)
        self.tick_minor_length_widget = self.createSpinBox(
            5, _min=1, prefix="length: ", callback=self.update_tick_params
        )

        minor_tick_controller_layout.addWidget(QtWidgets.QLabel("minor"))
        minor_tick_controller_layout.addWidget(self.tick_minor_width_widget)
        minor_tick_controller_layout.addWidget(self.tick_minor_length_widget)
        self.controlLayout.addLayout(major_tick_controller_layout)
        self.controlLayout.addLayout(minor_tick_controller_layout)

    def figure_ticks_controllers(self):
        self.getaxisUpdateFunction()
        
        tickAndFormatterLayout = QtWidgets.QFormLayout()
        self.tickLocatorWidget = self.createSpinBox(5, _min=2, width=50, callback=self.updateTicksAndFormatter)

        formatterLayout = QtWidgets.QHBoxLayout()
        
        self.fomartTickCheck = QtWidgets.QCheckBox()

        self.fomartTickCheck.setFixedHeight(25)
        self.tickFormatterWidget = QtWidgets.QLineEdit("{x:.0f}")
        self.tickFormatterWidget.setFixedWidth(100)
        self.tickFormatterWidget.returnPressed.connect(self.updateTicksAndFormatter)

        formatterLayout.addWidget(self.tickFormatterWidget)
        formatterLayout.addWidget(self.fomartTickCheck)

        tickAndFormatterLayout.addRow("tickLocator", self.tickLocatorWidget)
        tickAndFormatterLayout.addRow("tickFormatter", formatterLayout)

        axisControlLayout = QtWidgets.QHBoxLayout()

        self.ticklocatorfn = self.updatefn["ticklocator"]["major"]["x"]
        self.formatterfn = self.updatefn["formatter"]["major"]["x"]

        def makeTickAndFormatterFunction(_val):
            self.axisType = self.axistypeWidget.currentText()
            self.tickType = self.ticktypeWidget.currentText()
            if self.axisType == "both" or self.tickType == "both": return

            self.ticklocatorfn = self.updatefn["ticklocator"][self.tickType][self.axisType]
            self.formatterfn = self.updatefn["formatter"][self.tickType][self.axisType]

        self.axisType = "x"
        self.tickType = "major"

        self.axistypeWidget = QtWidgets.QComboBox()
        self.axistypeWidget.addItems(["x", "y", "both"])

        self.axistypeWidget.currentTextChanged.connect(makeTickAndFormatterFunction)
        self.ticktypeWidget = QtWidgets.QComboBox()
        self.ticktypeWidget.addItems(["major", "minor", "both"])
        self.ticktypeWidget.currentTextChanged.connect(makeTickAndFormatterFunction)

        self.major_minor_ticksize_controllers()

        axisControlLayout.addWidget(self.axistypeWidget)
        axisControlLayout.addWidget(self.ticktypeWidget)
        self.controlLayout.addLayout(axisControlLayout)
        self.controlLayout.addLayout(tickAndFormatterLayout)

    def figure_labels_controller(self) -> QtWidgets.QFormLayout:

        formLayout = QtWidgets.QFormLayout()
        savefilenameWidget = QtWidgets.QLineEdit(self.savefilename)
        def updateSavefilename(val): self.savefilename = val
        savefilenameWidget.textChanged.connect(updateSavefilename)

        # formLayout.addRow("savefile", savefilenameWidget)
        self.ax.set_title(self.figTitle, fontsize=16)
        self.ax.set_xlabel(self.figXlabel, fontsize=16)
        self.ax.set_ylabel(self.figYlabel, fontsize=16)

        titleWidgetGroup = self.figurelabelsWidgetMaker(self.figTitle, 16, "title")
        xlabelWidgetGroup = self.figurelabelsWidgetMaker(self.figXlabel, 16, "xlabel")
        ylabelWidgetGroup = self.figurelabelsWidgetMaker(self.figYlabel, 16, "ylabel")

        formLayout.addRow("title", titleWidgetGroup)
        formLayout.addRow("xlabel", xlabelWidgetGroup)
        formLayout.addRow("ylabel", ylabelWidgetGroup)
        self.draw()
        self.controlLayout.addLayout(formLayout)

    def update_figure_label_widgets_values(self, ax=None):
        ax = ax or self.ax

        self.titleWidget.setText(ax.get_title())
        self.xlabelWidget.setText(ax.get_xlabel())
        self.ylabelWidget.setText(ax.get_ylabel())

    def updateFigsizeDetails(self):
        self.figsize = (self.fig.get_figwidth(), self.fig.get_figheight())
        self.figsizeWidthWidget.setValue(self.figsize[0])
        self.figsizeHeightWidget.setValue(self.figsize[1])

    def resizeEvent(self, event):
        self.updateFigsizeDetails()

    def makefigsizeControlWidgets(self):

        def updateFigureSize(_val):
            self.figsize = [self.figsizeWidthWidget.value(), self.figsizeHeightWidget.value()]
            self.fig.set_size_inches(self.figsize)
            self.draw()
            canvas_width = self.figsize[0] * self.fig.dpi
            canvas_height = self.figsize[1] * self.fig.dpi
            self.canvasWidget.resize(canvas_width, canvas_height)

        layout = QtWidgets.QHBoxLayout()

        fig_kw = dict(_min=5, prefix="width: ", suffix=" in", _step=0.1, callback=updateFigureSize)
        self.figsizeWidthWidget = self.createSpinBox(6.4, **fig_kw)
        self.figsizeHeightWidget = self.createSpinBox(6.4, **fig_kw)

        layout.addWidget(self.figsizeWidthWidget)
        layout.addWidget(self.figsizeHeightWidget)

        def canvasAutoResize(resize):
            self.canvas_scroll.setWidgetResizable(resize)
            if resize:
                self.figsizeWidthWidget.setValue(self.fig.get_figwidth())
                self.figsizeHeightWidget.setValue(self.fig.get_figheight())
        autoResizeCanvas = QtWidgets.QCheckBox("auto-resize")
        autoResizeCanvas.setChecked(True)
        autoResizeCanvas.stateChanged.connect(canvasAutoResize)

        layout.addWidget(autoResizeCanvas)
        return layout

    def makeFigureLayout(
        self,
        fig: Optional[Figure] = None,
        canvas: Optional[FigureCanvasQTAgg] = None,
        figureArgs: Optional[dict[str, Any]] = {},

        defaultEvents: bool = True,
    ) -> None:

        # mpl.rcParams.update({'text.usetex': True, 'font.family': 'DejaVu Sans'})
        self.fig = fig if fig else Figure(**figureArgs)
        self.canvas = canvas if canvas else FigureCanvasQTAgg(self.fig)

        self.renderer = self.canvas.get_renderer()

        navbarLayoutWidget = QtWidgets.QHBoxLayout()
        figsizeControlWidgetsLayout = self.makefigsizeControlWidgets()
        navbarLayoutWidget.addWidget(NavigationToolbar2QT(self.canvas, self))
        navbarLayoutWidget.addLayout(figsizeControlWidgetsLayout)

        canvasLayout = QtWidgets.QVBoxLayout()
        canvasLayout.addWidget(self.canvas)

        self.canvasWidget = QtWidgets.QWidget()
        self.canvasWidget.setLayout(canvasLayout)

        self.canvas_scroll = QtWidgets.QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setWidget(self.canvasWidget)
        self.canvas_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.canvas_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        finalFigureLayout = QtWidgets.QVBoxLayout()
        finalFigureLayout.addLayout(navbarLayoutWidget)
        finalFigureLayout.addWidget(self.canvas_scroll)
        self.mainLayout.addLayout(finalFigureLayout, 4)

        if defaultEvents:
            self.canvas.mpl_connect("button_release_event", lambda e: self.canvas.setFocus())
            self.canvas.mpl_connect("key_press_event", lambda e: key_press_handler(e, self.canvas))

    def savefig(self):
        if not self.location.exists():
            self.showdialog("Error", f"Invalid location: {self.location}")
            return
        if not self.savefilename:
            return self.showdialog("Warning", f"Please enter a filename to save", "warning")

        filename = self.location / f"{self.savefilename}.{self.savefilefmt}"
        if filename.exists():
            ok = self.showYesorNo("Overwrite ?", f"Filename {filename.name} already exists in {self.location}")
            if not ok: return
        
        if self.savefilefmt == "pgf":

            mpl.rcParams.update({
                "pgf.texsystem": "pdflatex", 'font.family': 'DejaVu Sans',
                'text.usetex': True, 'pgf.rcfonts': False
            })
        self.fig.savefig(filename)
        self.showdialog("SAVED", f"{filename.name} saved in {self.location}")

    def createSpinBox(
        self,
        value: Union[float, int],
        _min: Union[float, int] = 0,
        _max: Union[float, int] = 500,
        _step: Union[float, int] = 1,
        prefix: str = None,
        suffix: str = None,
        setkey: str = None,
        width: int = None,
        callback: Callable = None
    ) -> Union[QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox]:

        spinbox = QtWidgets.QDoubleSpinBox() if isinstance(value, float) else QtWidgets.QSpinBox()
        spinbox.setValue(value)
        spinbox.setMinimum(_min)
        spinbox.setMaximum(_max)
        spinbox.setSingleStep(_step)
        spinbox.setKeyboardTracking(False)
        if prefix: spinbox.setPrefix(prefix)
        if suffix: spinbox.setSuffix(suffix)

        if setkey:
            setattr(self, setkey, value)
            spinbox.valueChanged.connect(lambda value: setattr(self, setkey, value))
        
        if width:
            spinbox.setFixedWidth(width)
        if callback:
            spinbox.valueChanged.connect(callback)
        
        return spinbox

    def update_axes_visible_status(self):
            
        self.tickToggleState = not self.tickToggleState
        self.ax.spines[self.spineWidget.currentText()].set_visible(self.tickToggleState)

        tickLabelStatus = {}
        
        if self.ticklabelToggleWidget.isChecked():
            tickLabelStatus[f"label{self.spineWidget.currentText()}"] = self.tickToggleState
        if self.tickToggleWidget.isChecked():
            tickLabelStatus[self.spineWidget.currentText()] = self.tickToggleState
        if tickLabelStatus:
            self.ax.tick_params(which="both", **tickLabelStatus, direction=self.ticks_direction)
        
        self.draw()

    def updateTickLabelSz(self, labelsize: int, ax: Axes=None, type: str=None):
        
        if not ax:
            ax = self.ax
        legend = ax.get_legend()
        
        self.update_tick_params(ax=ax)

        if not type:
            type = self.label_size_controller_widget.currentText()

        if type == "ticks":

            self.update_tick_params(labelsize=labelsize)
            
            ax.xaxis.get_offset_text().set_fontsize(labelsize - 2)
            ax.yaxis.get_offset_text().set_fontsize(labelsize - 2)

        elif type == "legend" and legend:
            for legend_text in legend.get_texts():
                legend_text.set_fontsize(labelsize)
                
        elif type == "legendTitle" and legend:
            legend.get_title().set_fontsize(labelsize)

        self.draw()

    def update_minorticks(self, on: bool, ax: Axes=None):

        if not ax: ax=self.ax

        if on:
            ax.minorticks_on()
            self.update_tick_params()
        else:
            ax.minorticks_off()
        self.draw()

    def figure_draw_controllers(self):

        controllerLayout = QtWidgets.QHBoxLayout()

        axesOptionsWidget = QtWidgets.QComboBox()
        axesOptionsWidget.addItems(self.getAxes.keys())

        def changeCurrentAxes(ax):
            self.ax = self.getAxes[ax]
            self.legend = self.ax.get_legend()
            self.update_figure_label_widgets_values()

        axesOptionsWidget.currentTextChanged.connect(changeCurrentAxes)
        updateFigureButton = QtWidgets.QPushButton("tight layout")
        updateFigureButton.clicked.connect(self.updatecanvas)

        self.minorticks_controller_widget = QtWidgets.QCheckBox("minorticks")
        self.minorticks_controller_widget.stateChanged.connect(self.update_minorticks)

        controllerLayout.addWidget(axesOptionsWidget)
        controllerLayout.addWidget(updateFigureButton)
        self.controlLayout.addLayout(controllerLayout)
        self.controlLayout.addWidget(self.minorticks_controller_widget)

    def figure_legend_controllers(self):

        def updateLegendState(state, type="toggle"):
            self.legend = self.ax.get_legend()
            if self.legend:
                if type == "toggle":
                    self.legend.set_visible(state)
                elif type == "dragg":
                    self.legend.set_draggable(state, use_blit=True)

                self.draw()

        controllerLayout = QtWidgets.QHBoxLayout()

        self.legendToggleCheckWidget = QtWidgets.QCheckBox("legend")
        self.legendToggleCheckWidget.stateChanged.connect(updateLegendState)

        self.legendDraggableCheckWidget = QtWidgets.QCheckBox("dragg")
        self.legendDraggableCheckWidget.stateChanged.connect(lambda state: updateLegendState(state, "dragg"))
        self.legendalpha: float = 0.5
        
        toggleLegendAlphaWidget = self.createSpinBox(0.5, _step=0.1, _max=1, prefix="alpha: ", setkey="legendalpha")

        controllerLayout.addWidget(self.legendToggleCheckWidget)
        controllerLayout.addWidget(self.legendDraggableCheckWidget)
        controllerLayout.addWidget(toggleLegendAlphaWidget)

        controllerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.controlLayout.addLayout(controllerLayout)

    def figure_axes_scaling_controller(self):
        
        controllerLayout = QtWidgets.QHBoxLayout()
        self.XlogScaleWidget = QtWidgets.QCheckBox("Xlog")
        def updateAxisScale(fn, scale):
            fn("log" if scale else "linear")
            self.draw()

        self.XlogScaleWidget.stateChanged.connect(lambda scale: updateAxisScale(self.ax.set_xscale, scale))
        self.YlogScaleWidget = QtWidgets.QCheckBox("Ylog")
        self.YlogScaleWidget.stateChanged.connect(lambda scale: updateAxisScale(self.ax.set_yscale, scale))

        controllerLayout.addWidget(self.XlogScaleWidget)
        controllerLayout.addWidget(self.YlogScaleWidget)
        controllerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        self.controlLayout.addLayout(controllerLayout)

    def figure_tick_format_controllers(self):

        controllerLayout = QtWidgets.QFormLayout()

        self.tick_label_fontsize_controller_widget = self.createSpinBox(
            16, _min=5, width=50, callback=self.updateTickLabelSz
        )
        
        self.tickFormatStyleWidget = QtWidgets.QComboBox()
        self.tickFormatStyleWidget.addItems(["plain", "sci"])

        def updateTickFormatStyle(style):
            self.formatterfn(plticker.ScalarFormatter())
            self.ax.ticklabel_format(axis=self.axisType, style=style)

            self.draw()

        self.tickFormatStyleWidget.currentTextChanged.connect(updateTickFormatStyle)
        self.label_size_controller_widget = QtWidgets.QComboBox()
        self.label_size_controller_widget.addItems(["ticks", "legend", "legendTitle"])

        label_size_layout = QtWidgets.QHBoxLayout()
        label_size_layout.addWidget(self.label_size_controller_widget)
        label_size_layout.addWidget(self.tick_label_fontsize_controller_widget)

        controllerLayout.addRow("fontsize", label_size_layout)
        controllerLayout.addRow("Tick format", self.tickFormatStyleWidget)
        self.controlLayout.addLayout(controllerLayout)

    def figure_axes_spine_and_tick_toggle_controllers(self):

        ticks_control_layout = QtWidgets.QHBoxLayout()

        self.ticks_direction: str = "in"
        ticks_direction_widget = QtWidgets.QComboBox()

        ticks_direction_widget.addItems(["in", "out", "inout"])
        def update_ticks_direction(val: str) -> None: 
            self.ticks_direction = val
            self.ax.tick_params(axis=self.axisType, which=self.tickType, direction=val)
            self.draw()

        ticks_direction_widget.currentTextChanged.connect(update_ticks_direction)
        # ticks_direction_widget.textChanged.connect(update_ticks_direction)

        toggleTickButton = QtWidgets.QPushButton("toggle")
        self.tickToggleState = True
        toggleTickButton.clicked.connect(self.update_axes_visible_status)

        ticks_control_layout.addWidget(QtWidgets.QLabel("Ticks: "))
        ticks_control_layout.addWidget(ticks_direction_widget)
        ticks_control_layout.addWidget(toggleTickButton)

        controllerLayout = QtWidgets.QHBoxLayout()
        
        directionCollections = ["bottom", "top", "left", "right"]

        self.spineWidget = QtWidgets.QComboBox()
        self.spineWidget.addItems(directionCollections)

        self.tickToggleWidget = QtWidgets.QCheckBox("tick")
        self.ticklabelToggleWidget = QtWidgets.QCheckBox("labels")
        
        controllerLayout.addWidget(self.spineWidget)
        controllerLayout.addWidget(self.tickToggleWidget)
        controllerLayout.addWidget(self.ticklabelToggleWidget)

        self.controlLayout.addLayout(ticks_control_layout)
        # self.controlLayout.addWidget(toggleTickButton)
        
        self.controlLayout.addLayout(controllerLayout)

    def figure_save_controllers(self):

        savefilenameWidget = QtWidgets.QLineEdit(self.savefilename)
        def updateSavefilename(val): self.savefilename = val
        savefilenameWidget.textChanged.connect(updateSavefilename)

        savefilenameWidget.returnPressed.connect(self.savefig)


        controllerLayout = QtWidgets.QHBoxLayout()
        self.savefilefmt = "pdf"

        savefmtOptionsWidget = QtWidgets.QComboBox()

        savefmtOptionsWidget.addItems(self.canvas.filetypes.keys())
        savefmtOptionsWidget.setCurrentText(self.savefilefmt)
        
        def changeSaveFmt(fmt): self.savefilefmt = fmt
        savefmtOptionsWidget.currentTextChanged.connect(changeSaveFmt)

        saveButtonWidget = QtWidgets.QPushButton("Save figure")
        saveButtonWidget.clicked.connect(self.savefig)

        controllerLayout.addWidget(savefmtOptionsWidget)
        controllerLayout.addWidget(saveButtonWidget)

        save_wdigets_final_layout = QtWidgets.QVBoxLayout()
        save_wdigets_final_layout.addWidget(QtWidgets.QLabel("Savefilename"))
        save_wdigets_final_layout.addWidget(savefilenameWidget)
        save_wdigets_final_layout.addLayout(controllerLayout)
        controlGroup = QtWidgets.QGroupBox()
        controlGroup.setLayout(save_wdigets_final_layout)
        self.controlLayout.addWidget(controlGroup)

    def align_full_layout(self, optimize):
        # pass
        self.figure_DPI_controller()
        self.figure_labels_controller()
        self.figure_draw_controllers()
        
        self.figure_legend_controllers()
        self.figure_axes_scaling_controller()
        self.figure_ticks_controllers()
        self.figure_tick_format_controllers()
        self.figure_axes_spine_and_tick_toggle_controllers()
        # self.figure_save_controllers()

        if optimize: self.optimize_figure()

    def optimize_figure(self):

        labelsize = self.tick_label_fontsize_controller_widget.value()
        
        for ax in self.axes:
            
            self.updateTickLabelSz(labelsize, ax=ax, type="ticks")
            self.update_tick_params(labelsize=labelsize)
            ax.tick_params(which="both", bottom=True, top=True, left=True, right=True, direction=self.ticks_direction)
            self.updateTickLabelSz(labelsize=labelsize-2, ax=ax, type="legend")
            self.updateTickLabelSz(labelsize, ax=ax, type="legendTitle")
            self.update_minorticks(True, ax)

            ax.set_title(ax.get_title(), fontsize=labelsize)
            ax.set_xlabel(ax.get_xlabel(), fontsize=labelsize)
            ax.set_ylabel(ax.get_ylabel(), fontsize=labelsize)

        self.minorticks_controller_widget.setChecked(True)
        self.update_figure_label_widgets_values()

    def createControlLayout(self, axes: Iterable[Axes] = [], attachControlLayout=True, optimize=False) -> None:

        self.controlLayout = QtWidgets.QVBoxLayout()
        self.legend = None
        if len(axes):
            self.axes = axes

        else:
            ax: Axes = self.fig.subplots()
            self.axes = [ax]

        self.getAxes: dict[str, Axes] = {f"ax{i}": ax for i, ax in enumerate(self.axes)}
        self.ax = self.getAxes["ax0"]

        if not self.ax:
            raise Exception("No axes in the plot")

        self.legend = self.ax.get_legend()
        self.align_full_layout(optimize)
        if attachControlLayout:
            self.showWidget()

    def showdialog(self, title="Info", msg="", type="info"):

        dialogBox = QtWidgets.QMessageBox(self)

        dialogBox.setWindowTitle(title)
        dialogBox.setText(msg)

        if type == "info":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Information)

        elif type == "warning":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)

        elif type == "critical":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)

        response = dialogBox.exec()

    def makeSlider(self, label="", ticks=True, bind_func: Callable[[int], None] = None):
        """Sliders range from 0-99"""

        slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        slider.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        if ticks:
            slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)
            slider.setTickInterval(10)

        slider.valueChanged[int].connect(bind_func)
        label = QtWidgets.QLabel(label)
        widget = QtWidgets.QHBoxLayout()
        widget.addWidget(label)
        widget.addWidget(slider)

        return widget

    def showYesorNo(self, title="Info", info=""):
        response = QtWidgets.QMessageBox.question(
            self, title, info, QtWidgets.QMessageBox.StandardButton.Yes, QtWidgets.QMessageBox.StandardButton.No
        )

        return response == QtWidgets.QMessageBox.StandardButton.Yes

    def makeLegendToggler(
        self, line_handler: dict[str, Union[Union[Container, Artist], Iterable[Union[Container, Artist]]]]
    ) -> None:

        self.legend = self.ax.legend()
        self.legendToggleCheckWidget.setChecked(True)
        for legline in self.legend.get_texts():
            legline.set_picker(True)

        self.canvas.mpl_connect("pick_event", lambda e: on_pick(e, line_handler, self))


def closeEvent(self, event):

    reply = QtWidgets.QMessageBox.question(
        self,
        "Window Close",
        "Are you sure you want to close the window?",
        QtWidgets.QMessageBox.StandardButton.Yes,
        QtWidgets.QMessageBox.StandardButton.No,
    )
    close = reply == QtWidgets.QMessageBox.StandardButton.Yes
    event.accept() if close else event.ignore()


def toggle_this_artist(artist: Union[Container, Artist], alpha: float) -> float:
    
    if not (isinstance(artist, Artist) or isinstance(artist, Container)):
        return print(f"unknown toggle method for this artist type\n{type(artist)}")
    set_this_alpha = alpha
    if isinstance(artist, Artist):
        set_this_alpha: float = alpha if artist.get_alpha() is None or artist.get_alpha() == 1 else 1
        artist.set_alpha(set_this_alpha)
    elif isinstance(artist, Container):
        for child in artist.get_children():
            set_this_alpha: float = alpha if child.get_alpha() is None or child.get_alpha() == 1 else 1
            child.set_alpha(set_this_alpha)

    return set_this_alpha


def on_pick(
    event,
    line_handler: dict[str, Union[Union[Container, Artist], Iterable[Union[Container, Artist]]]],
    widget: felionQtWindow
) -> None:

    picked_legend = event.artist

    if widget.legendDraggableCheckWidget.isChecked(): return
    if not isinstance(picked_legend, Text): return

    picked_line_handler = picked_legend.get_text()
    toggle_artist = line_handler[picked_line_handler]

    set_this_alpha = widget.legendalpha
    if isinstance(toggle_artist, Iterable):
        for artist in toggle_artist:
            set_this_alpha = toggle_this_artist(artist, widget.legendalpha)
    else:
        set_this_alpha = toggle_this_artist(toggle_artist, widget.legendalpha)

    picked_legend.set_alpha(0.5 if set_this_alpha < 1 else 1)
    widget.draw()
