import sys
import traceback
from pathlib import Path as pt
from types import TracebackType
from typing import Any, Callable, Iterable, Literal, Optional, Type, Union

from PyQt6.QtCore import Qt, QThreadPool
import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtGui import QIcon

import matplotlib as mpl

mpl.use("QtAgg")

from matplotlib.artist import Artist
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.container import Container
from matplotlib.figure import Figure

from matplotlib.axes import Axes
from matplotlib.backend_bases import key_press_handler
from matplotlib.legend import Legend
from matplotlib.text import Text
import matplotlib.ticker as plticker
from .utils.widgets import ShowDialog, AnotherWindow, iconfile, toggle_this_artist, closeEvent
from .utils.workers import Worker

import matplotlib.pyplot as plt
from .qt_material import QtStyleTools, list_themes


QApplication = QtWidgets.QApplication
qapp = QtWidgets.QApplication([])


def excepthook(etype, value, tb):
    tb = "".join(traceback.format_exception(etype, value, tb, limit=5))
    print("error catched!:", value, flush=True)
    print("error message:\n", tb, flush=True)
    ShowDialog(f"{etype.__name__}", tb, "critical")


sys.excepthook = excepthook


class felionQtWindow(QtWidgets.QMainWindow, QtStyleTools):
    def __init__(
        self,
        location: str = "",
        title: str = "felionQt-Figure",
        figTitle: str = "",
        figYlabel: str = "",
        figXlabel: str = "",
        savefilename: str = "",
        saveformat: str = "pdf",
        figDPI: int = 150,
        defaultEvents: bool = True,
        createControlLayout: bool = True,
        includeCloseEvent: bool = False,
        windowGeometry: tuple[int, int] = (900, 700),
        useTex: bool = False,
        style: str = "default",
        fontsize: int = 12,
        optimize: bool = False,
        ticks_direction: Literal["in", "out", "inout"] = "in",
        yscale: Literal["linear", "log"] = "linear",
        xscale: Literal["linear", "log"] = "linear",
        attachControlLayout=True,
        **kwargs: dict[str, Any],
    ) -> None:

        super().__init__()

        self._main = QtWidgets.QWidget()
        self.useTex = useTex
        self.qapp = qapp
        if style and style != "default":
            plt.style.use(style)

        mpl.rcParams.update(
            {
                "text.usetex": useTex,
                "lines.markersize": 4,
                "legend.frameon": False,
                "legend.labelspacing": 0.1,
                "legend.handletextpad": 0.5,
            }
        )

        if "mpl_kw" in kwargs:
            mpl.rcParams.update(kwargs["mpl_kw"])

        self.saveformat = saveformat
        self.figDPI = round(figDPI)
        self.fontsize = int(fontsize)
        self.ticks_direction = ticks_direction

        self.yscale = yscale
        self.xscale = xscale

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

        self.threadpool = QThreadPool()
        if includeCloseEvent:
            self.closeEvent = lambda event: closeEvent(self, event)

        figureArgs = {"dpi": figDPI}

        if "figureArgs" in kwargs:
            figureArgs = figureArgs | self.kwargs["figureArgs"]

        self.init_attributes()

        self.makeFigureLayout(figureArgs=figureArgs, defaultEvents=defaultEvents)

        if createControlLayout:
            self.createControlLayout(attachControlLayout=attachControlLayout, optimize=optimize)

    def init_attributes(self):

        self.titleWidget = QtWidgets.QLineEdit("")
        self.xlabelWidget = QtWidgets.QLineEdit("")
        self.ylabelWidget = QtWidgets.QLineEdit("")
        self.finalControlLayout = QtWidgets.QVBoxLayout()
        self.fixedControllerWidth = 270
        self.legend_picker_set = False
        self.line_handler = None
        self.picked_legend = None
        self.ctrl_pressed = False
        self.legend_edit_window = None

    def toggle_controller_layout(self):

        hidden_state = self.finalControlWidget.isHidden()
        self.finalControlWidget.setHidden(not hidden_state)
        button_txt = "Hide controllers" if hidden_state else "Show more controllers"
        self.toggle_controller_button.setText(button_txt)

    def attachControlLayout(self):

        self.controlLayout.addStretch()
        controlGroupBox = QtWidgets.QGroupBox()
        controlGroupBox.setLayout(self.controlLayout)

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(controlGroupBox)
        savecontrolGroup = self.figure_save_controllers()
        self.finalControlWidget = QtWidgets.QWidget()

        self.finalControlLayout.addWidget(scroll)
        self.finalControlLayout.addWidget(savecontrolGroup)

        self.finalControlWidget.setLayout(self.finalControlLayout)
        # self.finalControlWidget.setFixedWidth(self.fixedControllerWidth)
        self.mainLayout.addWidget(self.finalControlWidget, 1)
        self.toggle_controller_layout()

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

        dpiwidget = self.createSpinBox(value=self.figDPI, prefix="DPI: ", _min=100, _step=1, callback=changefigDPI)
        dpiwidget.setValue(self.figDPI)
        # self.controlLayout.addWidget(dpiwidget)
        return dpiwidget

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

        if self.axisType == "both" or self.tickType == "both":
            # self.ax.locator_params(tight=True, nbins=Nlocator)
            return

        if self.tickType == "minor":

            if self.axisType == "x":
                Nlocator = Nlocator * len(self.ax.get_xticks())
            elif self.axisType == "y":
                Nlocator = Nlocator * len(self.ax.get_yticks())

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

    def update_tick_params(self, _val=0, ax=None, draw=True, **kwargs):
        ax = ax or self.ax
        ax.tick_params(
            which="major",
            width=self.tick_major_width_widget.value(),
            length=self.tick_major_length_widget.value(),
            **kwargs,
        )
        ax.tick_params(
            which="minor",
            width=self.tick_minor_width_widget.value(),
            length=self.tick_minor_length_widget.value(),
            **kwargs,
        )
        if draw:
            self.draw()

    def major_minor_ticksize_controllers(self):

        major_tick_controller_layout = QtWidgets.QHBoxLayout()

        self.tick_major_width_widget = self.createSpinBox(2, _min=1, prefix="width: ", callback=self.update_tick_params)
        self.tick_major_length_widget = self.createSpinBox(
            5, _min=1, prefix="length: ", callback=self.update_tick_params
        )
        major_tick_controller_layout.addWidget(QtWidgets.QLabel("major"))

        major_tick_controller_layout.addWidget(self.tick_major_width_widget)
        major_tick_controller_layout.addWidget(self.tick_major_length_widget)

        minor_tick_controller_layout = QtWidgets.QHBoxLayout()

        self.tick_minor_width_widget = self.createSpinBox(1, _min=1, prefix="width: ", callback=self.update_tick_params)
        self.tick_minor_length_widget = self.createSpinBox(
            3, _min=1, prefix="length: ", callback=self.update_tick_params
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

        self.tickIntervalWidget = QtWidgets.QLineEdit("")
        self.tickIntervalWidget.setPlaceholderText("Enter ticks interval")

        def update_tick_interval():
            tick_interval = self.tickIntervalWidget.text()

            if not tick_interval:
                return
            update_tick_function = self.updatefn["ticklocator"][self.tickType][self.axisType]
            update_tick_function(plticker.MultipleLocator(int(tick_interval)))
            self.draw()

        self.tickIntervalWidget.returnPressed.connect(update_tick_interval)
        formatterLayout = QtWidgets.QHBoxLayout()
        self.fomartTickCheck = QtWidgets.QCheckBox()

        self.fomartTickCheck.setFixedHeight(25)
        self.tickFormatterWidget = QtWidgets.QLineEdit("{x:.0f}")
        self.tickFormatterWidget.setFixedWidth(100)
        self.tickFormatterWidget.returnPressed.connect(self.updateTicksAndFormatter)

        formatterLayout.addWidget(self.tickFormatterWidget)
        formatterLayout.addWidget(self.fomartTickCheck)

        tickAndFormatterLayout.addRow("tickInterval", self.tickIntervalWidget)
        tickAndFormatterLayout.addRow("tickLocator", self.tickLocatorWidget)
        tickAndFormatterLayout.addRow("tickFormatter", formatterLayout)

        axisControlLayout = QtWidgets.QHBoxLayout()

        self.ticklocatorfn = self.updatefn["ticklocator"]["major"]["x"]
        self.formatterfn = self.updatefn["formatter"]["major"]["x"]

        def makeTickAndFormatterFunction(_val):
            self.axisType = self.axistypeWidget.currentText()
            self.tickType = self.ticktypeWidget.currentText()
            if self.axisType == "both" or self.tickType == "both":
                return

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

        def updateSavefilename(val):
            self.savefilename = val

        savefilenameWidget.textChanged.connect(updateSavefilename)

        # fontsize = 10
        self.ax.set_title(self.figTitle, fontsize=self.fontsize)
        self.ax.set_xlabel(self.figXlabel, fontsize=self.fontsize)
        self.ax.set_ylabel(self.figYlabel, fontsize=self.fontsize)

        titleWidgetGroup = self.figurelabelsWidgetMaker(self.figTitle, self.fontsize, "title")
        xlabelWidgetGroup = self.figurelabelsWidgetMaker(self.figXlabel, self.fontsize, "xlabel")
        ylabelWidgetGroup = self.figurelabelsWidgetMaker(self.figYlabel, self.fontsize, "ylabel")

        formLayout.addRow("title", titleWidgetGroup)
        formLayout.addRow("xlabel", xlabelWidgetGroup)
        formLayout.addRow("ylabel", ylabelWidgetGroup)
        # self.draw()

        self.controlLayout.addLayout(formLayout)

    def update_figure_label_widgets_values(self, ax=None):

        ax = ax or self.ax
        self.titleWidget.setText(ax.get_title())
        self.xlabelWidget.setText(ax.get_xlabel())
        self.ylabelWidget.setText(ax.get_ylabel())

    def updateFigsizeDetails(self, event=None):
        self.figsize = (self.fig.get_figwidth(), self.fig.get_figheight())

        self.figsizeWidthWidget.setValue(self.figsize[0])
        self.figsizeHeightWidget.setValue(self.figsize[1])

    # def resizeEvent(self, event):
    #     self.updateFigsizeDetails()

    def makefigsizeControlWidgets(self):
        def updateFigureSize(_val):

            self.figsize = (self.figsizeWidthWidget.value(), self.figsizeHeightWidget.value())
            self.fig.set_size_inches(self.figsize)
            self.draw()

            canvas_width = self.figsize[0] * self.fig.dpi
            canvas_height = self.figsize[1] * self.fig.dpi

            self.canvasWidget.resize(int(canvas_width), int(canvas_height))

        layout = QtWidgets.QHBoxLayout()

        fig_kw = dict(_min=2, suffix=" in", _step=0.1, callback=updateFigureSize)
        self.figsizeWidthWidget = self.createSpinBox(6.4, prefix="width: ", **fig_kw)
        self.figsizeHeightWidget = self.createSpinBox(6.4, prefix="height: ", **fig_kw)

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

    def create_navbar_layout(self):

        self.navbar_layout = QtWidgets.QVBoxLayout()
        self.navbar_layout.addWidget(NavigationToolbar2QT(self.canvas, self))

        navbar_controller_layout = QtWidgets.QHBoxLayout()

        navbar_figure_tight_layout_button = QtWidgets.QPushButton("tight layout")
        navbar_figure_tight_layout_button.clicked.connect(lambda: (self.fig.tight_layout(), self.draw()))

        canvas_draw_button = QtWidgets.QPushButton("Re-draw")
        canvas_draw_button.clicked.connect(self.draw)

        # choose_theme_widget = QtWidgets.QComboBox()
        # choose_theme_widget.addItems(list_themes())
        # choose_theme_widget.addItems(["default", "theme"])

        current_theme = pt(__file__).parent / "themes/theme.xml"
        current_theme = current_theme.resolve().__str__()

        # choose_theme_widget.setCurrentText(current_theme)
        # template = pt(__file__).parent / "themes/material.qt.css"
        # self.apply_stylesheet(self, current_theme, template=template)
        # choose_theme_widget.currentTextChanged.connect(lambda theme: self.apply_stylesheet(self, theme, template=template))

        # self.apply_stylesheet
        get_figsize_button = QtWidgets.QPushButton("Get figsize")
        get_figsize_button.clicked.connect(self.updateFigsizeDetails)

        figsize_adjust_layout = self.makefigsizeControlWidgets()
        dpiwidget = self.figure_DPI_controller()

        self.toggle_controller_button = QtWidgets.QPushButton("Controller")
        self.toggle_controller_button.clicked.connect(self.toggle_controller_layout)

        # navbar_controller_layout.addWidget(choose_theme_widget)

        navbar_controller_layout.addWidget(get_figsize_button)
        navbar_controller_layout.addLayout(figsize_adjust_layout)
        navbar_controller_layout.addWidget(dpiwidget)
        navbar_controller_layout.addWidget(canvas_draw_button)
        navbar_controller_layout.addWidget(navbar_figure_tight_layout_button)
        navbar_controller_layout.addWidget(self.toggle_controller_button)

        navbar_controller_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        navbar_controller_widget = QtWidgets.QWidget()
        navbar_controller_widget.setLayout(navbar_controller_layout)

        navbar_controller_scroll = QtWidgets.QScrollArea()
        navbar_controller_scroll.setWidgetResizable(True)
        navbar_controller_scroll.setWidget(navbar_controller_widget)
        navbar_controller_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        navbar_controller_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        navbar_controller_scroll.setFixedHeight(45)
        # navbar_controller_scroll.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.navbar_layout.addWidget(navbar_controller_scroll)

        # self.navbar_layout.addLayout(navbar_controller_layout)

    def create_figure_canvas_layout(self):
        canvasLayout = QtWidgets.QVBoxLayout()
        canvasLayout.addWidget(self.canvas)

        self.canvasWidget = QtWidgets.QWidget()
        self.canvasWidget.setLayout(canvasLayout)

        self.canvas_scroll = QtWidgets.QScrollArea()
        self.canvas_scroll.setWidgetResizable(True)
        self.canvas_scroll.setWidget(self.canvasWidget)

        self.canvas_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.canvas_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def makeFigureLayout(
        self,
        fig: Optional[Figure] = None,
        canvas: Optional[FigureCanvasQTAgg] = None,
        figureArgs: Optional[dict[str, Any]] = {},
        defaultEvents: bool = True,
    ) -> None:

        self.fig = fig if fig else Figure(**figureArgs)

        self.canvas = canvas if canvas else FigureCanvasQTAgg(self.fig)

        self.create_figure_canvas_layout()
        self.create_navbar_layout()

        final_figure_layout = QtWidgets.QVBoxLayout()
        final_figure_layout.addLayout(self.navbar_layout)
        final_figure_layout.addWidget(self.canvas_scroll)
        self.final_figure_widget = QtWidgets.QWidget()
        self.final_figure_widget.setLayout(final_figure_layout)
        self.final_figure_widget.setMinimumWidth(500)
        self.final_figure_widget.setMinimumHeight(500)
        # self.mainLayout.addLayout(final_figure_layout, 4)
        self.mainLayout.addWidget(self.final_figure_widget, 3)

        if defaultEvents:
            self.canvas.mpl_connect("button_release_event", lambda e: self.canvas.setFocus())
            self.canvas.mpl_connect("key_press_event", lambda e: key_press_handler(e, self.canvas))

    def save_file_worker(self, filename):

        if self.saveformat == "pgf":

            mpl_kw = {"pgf.texsystem": "pdflatex", "text.usetex": True, "pgf.rcfonts": False}

            @mpl.rc_context(mpl_kw)
            def savefileFunc(filename, *args, **kwargs):
                self.save_figure_status_widget.setText("Saving...")

                self.fig.savefig(filename, *args, format=self.saveformat, **kwargs)

        else:

            def savefileFunc(filename, *args, **kwargs):
                self.save_figure_status_widget.setText("Saving...")
                self.fig.savefig(filename, *args, format=self.saveformat, **kwargs)

        worker = Worker(savefileFunc, filename)  # fn, args, kwargs
        worker.signals.result.connect(lambda s: print(s))

        def on_complete():
            nonlocal error_occured
            if not error_occured:
                self.save_figure_status_widget.setText("figure saved.")
                self.showdialog("Saved", f"Saved to {filename.name}")
            else:
                self.save_figure_status_widget.setText("Error saving figure.")

        worker.signals.finished.connect(on_complete)
        error_occured = False

        def error_while_saving_figure(err: tuple[Type[BaseException], BaseException, TracebackType]) -> None:
            nonlocal error_occured
            error_occured = True
            excepthook(*err)

        worker.signals.error.connect(error_while_saving_figure)
        # worker.signals.progress.connect(self.progress_fn)
        self.threadpool.start(worker)

    def savefig(self):

        if not self.location.exists():

            # self.showdialog("Error", f"Invalid location: {self.location}")
            create_directory = self.showYesorNo("location does not exist", "Do you want to create it?")
            if create_directory:
                self.location.mkdir()
            else:
                return

        if not self.savefilename:
            return self.showdialog("Warning", f"Please enter a filename to save", "warning")

        filename = self.location / f"{self.savefilename}.{self.saveformat}"

        if filename.exists():
            ok = self.showYesorNo("Overwrite ?", f"Filename {filename.name} already exists in {self.location}")
            if not ok:
                return

        self.save_file_worker(filename)

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
        callback: Callable[[Union[int, float]], Any] = None,
    ) -> Union[QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox]:

        spinbox = QtWidgets.QDoubleSpinBox() if isinstance(value, float) else QtWidgets.QSpinBox()
        # if value>50: print(f"{value=}")
        spinbox.setValue(value)
        spinbox.setMinimum(_min)
        spinbox.setMaximum(_max)
        spinbox.setSingleStep(_step)
        spinbox.setKeyboardTracking(False)
        if prefix is not None:
            spinbox.setPrefix(prefix)
        if suffix is not None:
            spinbox.setSuffix(suffix)

        if setkey is not None:
            setattr(self, setkey, value)
            spinbox.valueChanged.connect(lambda value: setattr(self, setkey, value))

        if width is not None:
            spinbox.setFixedWidth(width)
        if callback is not None:
            spinbox.valueChanged.connect(callback)
        # print(value, spinbox.value())
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

    def updateTickLabelSz(self, labelsize: int, ax: Axes = None, type: str = None):

        ax = ax or self.ax
        legend: Legend = ax.get_legend()

        self.ax.add_callback(lambda artist: print(artist, flush=True))
        self.update_tick_params(ax=ax)

        type = type or self.label_size_controller_widget.currentText()
        if type == "ticks":
            print(f"updating ticks labelsize: {labelsize}")
            self.update_tick_params(labelsize=labelsize)
            ax.xaxis.get_offset_text().set_fontsize(labelsize - 2)
            ax.yaxis.get_offset_text().set_fontsize(labelsize - 2)
        elif type == "legend" and legend:
            print(f"updating labelsize: {labelsize}")
            for legend_text in legend.get_texts():
                legend_text.set_fontsize(labelsize)
        elif type == "legendTitle" and legend:
            print(f"updating legendTitle labelsize: {labelsize}")
            legend.get_title().set_fontsize(labelsize)
        self.draw()

    def update_minorticks(self, on: bool, ax: Axes = None):
        ax = ax or self.ax

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
        tight_layout_button = QtWidgets.QPushButton("tight layout")
        tight_layout_button.clicked.connect(self.updatecanvas)

        controllerLayout.addWidget(axesOptionsWidget)
        controllerLayout.addWidget(tight_layout_button)
        self.controlLayout.addLayout(controllerLayout)

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

        # controllerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
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
        if self.yscale == "log":
            self.YlogScaleWidget.setChecked(True)

        if self.xscale == "log":
            self.XlogScaleWidget.setChecked(True)

        self.minorticks_controller_widget = QtWidgets.QCheckBox("minorticks")
        self.minorticks_controller_widget.stateChanged.connect(self.update_minorticks)

        controllerLayout.addWidget(self.XlogScaleWidget)

        controllerLayout.addWidget(self.YlogScaleWidget)

        controllerLayout.addWidget(self.minorticks_controller_widget)
        # controllerLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.controlLayout.addLayout(controllerLayout)

    def set_bound_controller_values(self):
        def set_min_max_val(widget: QtWidgets.QDoubleSpinBox, val: float):

            if val < 0:
                return
            factor = 10 if val == 0 else val * 10
            _min = val - factor
            _max = val + factor

            widget.setMinimum(_min)
            widget.setMaximum(_max)
            widget.setValue(val)

        xbound: tuple[float, float] = self.ax.get_xbound()
        ybound: tuple[float, float] = self.ax.get_ybound()
        print(f"{xbound=}\n{ybound=}", flush=True)
        set_min_max_val(self.xbound_lower_widget, xbound[0])
        set_min_max_val(self.xbound_upper_widget, xbound[1])
        set_min_max_val(self.ybound_lower_widget, ybound[0])
        set_min_max_val(self.ybound_upper_widget, ybound[1])

    def create_minmax_controller(self, calltype: str, axis: str = "x", draw=True):

        main_widget = QtWidgets.QDoubleSpinBox()

        main_widget.setKeyboardTracking(False)

        def updated_callback(val: float):
            kwargs = {f"{calltype}": val}
            fn = self.ax.set_xbound if axis == "x" else self.ax.set_ybound
            fn(**kwargs)
            if draw:
                self.draw()

        main_widget.valueChanged.connect(updated_callback)
        return main_widget

    def layout_of_control_this_widget(self, this_widget: QtWidgets.QDoubleSpinBox):

        layout = QtWidgets.QHBoxLayout()
        lower_limit_widget = QtWidgets.QLineEdit("")
        lower_limit_widget.textChanged.connect(lambda val: this_widget.setMinimum(float(val)))
        upper_limit_widget = QtWidgets.QLineEdit("")
        lower_limit_widget.textChanged.connect(lambda val: this_widget.setMaximum(float(val)))
        stepsize_widget = QtWidgets.QLineEdit("")
        lower_limit_widget.textChanged.connect(lambda val: this_widget.setSingleStep(float(val)))

        layout.addWidget(lower_limit_widget)
        layout.addWidget(upper_limit_widget)
        layout.addWidget(stepsize_widget)

        return layout

    def figure_invert_axes(self):
        controlLayout = QtWidgets.QHBoxLayout()
        xaxis_invert_button_widget = QtWidgets.QPushButton("Invert X-axis")
        xaxis_invert_button_widget.clicked.connect(lambda: (self.ax.invert_xaxis(), self.draw()))
        yaxis_invert_button_widget = QtWidgets.QPushButton("Invert Y-axis")
        yaxis_invert_button_widget.clicked.connect(lambda: (self.ax.invert_yaxis(), self.draw()))

        controlLayout.addWidget(xaxis_invert_button_widget)
        controlLayout.addWidget(yaxis_invert_button_widget)
        self.controlLayout.addLayout(controlLayout)

    def figure_axes_bound_controller(self):

        bound_layout = QtWidgets.QVBoxLayout()

        update_bound_values = QtWidgets.QPushButton("GET XY bound")
        update_bound_values.clicked.connect(self.set_bound_controller_values)

        bound_layout.addWidget(update_bound_values)

        xbound_layout = QtWidgets.QHBoxLayout()
        xbound_layout.addWidget(QtWidgets.QLabel("xbound"))

        ybound_layout = QtWidgets.QHBoxLayout()
        ybound_layout.addWidget(QtWidgets.QLabel("ybound"))

        self.xbound_lower_widget = self.create_minmax_controller("lower", axis="x")
        self.xbound_upper_widget = self.create_minmax_controller("upper", axis="x")

        self.ybound_lower_widget = self.create_minmax_controller("lower", axis="y")
        self.ybound_upper_widget = self.create_minmax_controller("upper", axis="y")

        xbound_layout.addWidget(self.xbound_lower_widget)
        xbound_layout.addWidget(self.xbound_upper_widget)

        ybound_layout.addWidget(self.ybound_lower_widget)
        ybound_layout.addWidget(self.ybound_upper_widget)

        bound_layout.addLayout(xbound_layout)
        bound_layout.addLayout(ybound_layout)

        self.controlLayout.addLayout(bound_layout)

    def figure_tick_format_controllers(self):

        controllerLayout = QtWidgets.QFormLayout()

        self.tick_label_fontsize_controller_widget = self.createSpinBox(
            value=int(self.fontsize), _min=5, width=50, callback=self.updateTickLabelSz
        )

        self.tickFormatStyleWidget = QtWidgets.QComboBox()
        self.tickFormatStyleWidget.addItems(["plain", "sci"])

        def updateTickFormatStyle(style):
            self.formatterfn(plticker.ScalarFormatter())
            self.ax.ticklabel_format(axis=self.axisType, style=style, scilimits=(0, 0))
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
        self.ticks_direction_widget = QtWidgets.QComboBox()

        self.ticks_direction_widget.addItems(["in", "out", "inout"])

        def update_ticks_direction(val: str) -> None:
            self.ticks_direction = val
            self.ax.tick_params(axis=self.axisType, which=self.tickType, direction=val)
            self.draw()

        self.ticks_direction_widget.currentTextChanged.connect(update_ticks_direction)
        self.ticks_direction_widget.setCurrentText(self.ticks_direction)

        toggleTickButton = QtWidgets.QPushButton("toggle")
        self.tickToggleState = True
        toggleTickButton.clicked.connect(self.update_axes_visible_status)

        ticks_control_layout.addWidget(QtWidgets.QLabel("Ticks: "))
        ticks_control_layout.addWidget(self.ticks_direction_widget)
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

    def browse_save_location(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, 'Browse save location"', self.location.__str__())
        if directory:
            self.location = pt(directory).resolve()
            self.location_line_edit.setText(self.location.__str__())

    def figure_save_controllers(self):

        savefilenameWidget = QtWidgets.QLineEdit(self.savefilename)
        savefilenameWidget.setPlaceholderText("Enter filename to save...")

        def updateSavefilename(val):
            self.savefilename = val

        savefilenameWidget.textChanged.connect(updateSavefilename)
        savefilenameWidget.setToolTip("save filename")
        savefilenameWidget.returnPressed.connect(self.savefig)

        controllerLayout = QtWidgets.QHBoxLayout()

        savefmtOptionsWidget = QtWidgets.QComboBox()
        savefmtOptionsWidget.addItems(self.canvas.filetypes.keys())
        savefmtOptionsWidget.setCurrentText(self.saveformat)

        def changeSaveFmt(fmt):
            self.saveformat = fmt

        savefmtOptionsWidget.currentTextChanged.connect(changeSaveFmt)

        saveButtonWidget = QtWidgets.QPushButton("Save figure")
        saveButtonWidget.setProperty("class", "success")
        saveButtonWidget.clicked.connect(self.savefig)

        controllerLayout.addWidget(savefmtOptionsWidget)
        controllerLayout.addWidget(saveButtonWidget)

        save_location_control_widget = QtWidgets.QHBoxLayout()

        self.location_line_edit = QtWidgets.QLineEdit(self.location.__str__())
        self.location_line_edit.setReadOnly(True)
        self.location_line_edit.setToolTip("save location")

        browse_save_location_button = QtWidgets.QPushButton("Browse")
        browse_save_location_button.clicked.connect(self.browse_save_location)

        save_location_control_widget.addWidget(self.location_line_edit)
        save_location_control_widget.addWidget(browse_save_location_button)

        save_wdigets_final_layout = QtWidgets.QVBoxLayout()
        save_wdigets_final_layout.addLayout(save_location_control_widget)
        save_wdigets_final_layout.addWidget(savefilenameWidget)
        save_wdigets_final_layout.addLayout(controllerLayout)
        self.save_figure_status_widget = QtWidgets.QLabel("")
        save_wdigets_final_layout.addWidget(self.save_figure_status_widget)
        savecontrolGroup = QtWidgets.QGroupBox()
        savecontrolGroup.setLayout(save_wdigets_final_layout)
        # self.controlLayout.addWidget(savecontrolGroup)
        return savecontrolGroup

    def align_full_layout(self, optimize):

        self.figure_labels_controller()
        self.figure_draw_controllers()
        self.figure_legend_controllers()
        self.figure_axes_scaling_controller()
        self.figure_invert_axes()
        self.figure_axes_bound_controller()
        self.figure_ticks_controllers()
        self.figure_tick_format_controllers()
        self.figure_axes_spine_and_tick_toggle_controllers()
        if optimize:
            self.optimize_figure()

    def optimize_figure(self):

        labelsize = self.tick_label_fontsize_controller_widget.value()
        fontsize: int = self.titleFontWidget.value()
        for ax in self.axes:

            self.update_tick_params(ax=ax)
            ax.tick_params(which="both", direction=self.ticks_direction, labelsize=labelsize - 1)
            ax.minorticks_on()
            self.update_tick_params(ax=ax)
            ax.set_title(ax.get_title(), fontsize=fontsize)
            ax.set_xlabel(ax.get_xlabel(), fontsize=fontsize)
            ax.set_ylabel(ax.get_ylabel(), fontsize=fontsize)

            legend = ax.get_legend()

            if not legend:
                legend = ax.legend()

            legend_title = legend.get_title()
            legend_title.set_fontsize(labelsize)
            for legend_txt in legend.get_texts():
                legend_txt.set_fontsize(labelsize - 1)

            self.draw()

        self.minorticks_controller_widget.setChecked(True)
        self.update_figure_label_widgets_values()
        self.set_bound_controller_values()
        self.updateFigsizeDetails()

    def createControlLayout(self, axes: Iterable[Axes] = (), attachControlLayout=False, optimize=False) -> None:

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
            self.attachControlLayout()

    def showdialog(self, title="Info", msg="", type: Literal["info", "warning", "critical"] = "info"):
        dialogBox = QtWidgets.QMessageBox(self)
        dialogBox.setWindowTitle(title)
        dialogBox.setText(msg)

        if type == "info":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Information)
        elif type == "warning":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        elif type == "critical":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)

        dialogBox.exec()

    def makeSlider(
        self,
        label: str = "",
        value: Union[float, int] = 0,
        _min: Union[float, int] = 0,
        _max: Union[float, int] = None,
        decimals: int = 2,
        ticks: bool = False,
        callback: Callable[[Union[int, float]], Any] = None,
    ) -> tuple[QtWidgets.QHBoxLayout, Union[QtWidgets.QSpinBox, QtWidgets.QDoubleSpinBox]]:

        _max = _max or value * 5
        factor = 10**decimals
        slider = QtWidgets.QSlider(
            orientation=Qt.Orientation.Horizontal, singleStep=1, maximum=int(_max * factor), minimum=int(_min * factor)
        )

        if ticks:
            slider.setTickPosition(QtWidgets.QSlider.TickPosition.TicksBelow)

        if isinstance(value, int):
            spinbox = QtWidgets.QSpinBox(minimum=int(_min), maximum=int(_max))
            slider.valueChanged.connect(lambda val: spinbox.setValue(int(val / factor)))

        else:

            spinbox = QtWidgets.QDoubleSpinBox(
                maximum=_max,
                minimum=_min,
                decimals=decimals,
                singleStep=0.025 * _max,
            )

            slider.valueChanged.connect(lambda val: spinbox.setValue(val / factor))

        def updated_callback(val):
            slider.setValue(int(val * factor))
            if callback:
                callback(val)

        spinbox.setValue(value)
        slider.setValue(int(value * factor))

        spinbox.valueChanged.connect(updated_callback)

        layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel(label)

        layout.addWidget(label, 1)
        layout.addWidget(slider, 5)
        layout.addWidget(spinbox, 2)
        # layout.setAlignment(spinbox, Qt.AlignmentFlag.AlignLeft)

        return layout, spinbox

    def showYesorNo(self, title="Info", info=""):
        response = QtWidgets.QMessageBox.question(
            self, title, info, QtWidgets.QMessageBox.StandardButton.Yes, QtWidgets.QMessageBox.StandardButton.No
        )
        return response == QtWidgets.QMessageBox.StandardButton.Yes

    def on_pick(self, event) -> None:

        self.picked_legend = event.artist
        if self.ctrl_pressed:
            if isinstance(self.picked_legend, Text):
                return self.show_legend_edit_window()

        if self.legendDraggableCheckWidget.isChecked():
            return

        if not isinstance(self.picked_legend, Text):
            return

        if not self.line_handler:
            return

        picked_line_handler = self.picked_legend.get_text()
        toggle_artist = self.line_handler[picked_line_handler]

        set_this_alpha = self.legendalpha

        if isinstance(toggle_artist, Iterable) and not isinstance(toggle_artist, Container):
            for artist in toggle_artist:
                set_this_alpha = toggle_this_artist(artist, self.legendalpha)
        else:
            set_this_alpha = toggle_this_artist(toggle_artist, self.legendalpha)

        self.picked_legend.set_alpha(0.5 if set_this_alpha < 1 else 1)

        self.draw()

    def show_legend_edit_window(self):
        current_text: Text = self.picked_legend.get_text()
        if isinstance(self.legend_edit_window, AnotherWindow):
            self.legend_edit_window.edit_box_widget.setText(current_text)
            self.legend_edit_window.show()
            self.legend_edit_window.activateWindow()
            self.legend_edit_window.raise_()

    def edit_legend(self):

        if self.picked_legend is not None:
            current_text: Text = self.picked_legend.get_text()
            new_text = self.legend_edit_window.edit_box_widget.text()
            new_text = new_text.strip()

            if new_text and new_text != current_text:
                self.picked_legend.set_text(new_text)
                self.draw()

                if self.line_handler:
                    self.line_handler[new_text] = self.line_handler[current_text]
                    del self.line_handler[current_text]

        self.legend_edit_window.close()

    def make_legend_editor(self):

        self.ctrl_pressed = False

        def register_ctrl_press_button(e):
            if e.key == "control":
                self.ctrl_pressed = True

        self.canvas.mpl_connect("key_press_event", register_ctrl_press_button)

        def deregister_ctrl_press_button(e):
            self.ctrl_pressed = False

        self.canvas.mpl_connect("key_release_event", deregister_ctrl_press_button)

        if self.legend_edit_window is None:
            self.legend_edit_window = AnotherWindow()

            def edit_window_closeEvent(event):
                self.ctrl_pressed = False

            self.legend_edit_window.closeEvent = edit_window_closeEvent
        self.legend_edit_window.save_button_widget.clicked.connect(self.edit_legend)
        self.legend_edit_window.edit_box_widget.returnPressed.connect(self.edit_legend)

    def makeLegendToggler(self, line_handler: dict[str, Union[Container, Artist]] = None, edit_legend=True) -> None:
        self.line_handler = line_handler
        self.legend = self.ax.get_legend()
        if not self.legend:
            self.legend = self.ax.legend()

        self.legendToggleCheckWidget.setChecked(True)
        for legline in self.legend.get_texts():
            legline.set_picker(True)

        self.picked_legend = None
        self.canvas.mpl_connect("pick_event", self.on_pick)
        self.legend_picker_set = True
        if edit_legend:
            self.make_legend_editor()
