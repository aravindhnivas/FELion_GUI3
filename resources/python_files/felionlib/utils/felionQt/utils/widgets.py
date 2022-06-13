import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path as pt
from matplotlib.artist import Artist
from matplotlib.text import Text

# from matplotlib.lines import Line2D
from matplotlib.collections import PolyCollection, Collection
from matplotlib.container import ErrorbarContainer, Container
from typing import Union
import felionlib

# filepath = pt(felionQt.__file__).parent.resolve()
iconfile = pt(felionlib.__file__).parent / "../icons/icon.ico"


class ShowDialog(QtWidgets.QDialog):
    def __init__(self, title="Info", info="", type="info", parent=None):

        super().__init__(parent)
        dialogBox = QtWidgets.QMessageBox(self)
        self.setWindowIcon(QIcon(iconfile.resolve().__str__()))

        dialogBox.setWindowTitle(title)
        dialogBox.setText(info)

        if type == "info":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Information)

        elif type == "warning":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Warning)

        elif type == "critical":
            dialogBox.setIcon(QtWidgets.QMessageBox.Icon.Critical)

        dialogBox.exec()


class AnotherWindow(QtWidgets.QWidget):
    def __init__(self, title="EDIT legend"):
        super().__init__()
        self.setWindowTitle(title)

        self.setWindowIcon(QIcon(iconfile.resolve().__str__()))
        self.resize(300, 100)
        self.layout = QtWidgets.QVBoxLayout()
        self.edit_box_widget = QtWidgets.QLineEdit()
        self.save_button_widget = QtWidgets.QPushButton("Save")

        self.layout.addWidget(self.edit_box_widget)
        self.layout.addWidget(self.save_button_widget)
        self.layout.setAlignment(self.save_button_widget, Qt.AlignmentFlag.AlignRight)
        self.layout.addStretch()
        self.setLayout(self.layout)

        self.setMaximumHeight(100)
        self.setMaximumWidth(500)


def closeEvent(self, event):

    reply = QtWidgets.QMessageBox.question(
        self,
        "Window Close",
        "Are you sure you want to close the window?",
        QtWidgets.QMessageBox.StandardButton.Yes,
        QtWidgets.QMessageBox.StandardButton.No,
    )
    close = reply == QtWidgets.QtWidgets.QMessageBox.StandardButton.Yes
    event.accept() if close else event.ignore()


def toggle_this_artist(artist: Union[Artist, list, tuple], alpha: float, legend: Text = None) -> float:
    # set_this_alpha = alpha

    if isinstance(artist, list) or isinstance(artist, tuple):
        for child in artist:
            toggle_this_artist(child, alpha, legend)
        return

    set_this_alpha: float = alpha if artist.get_alpha() is None or artist.get_alpha() == 1 else 1
    artist.set_alpha(set_this_alpha)

    if legend is not None:
        # print(f"{legend=}", flush=True)
        legend.set_alpha(0.5 if set_this_alpha < 1 else 1)
    # if isinstance(artist, Artist) or isinstance(artist, PolyCollection):
    #     set_this_alpha: float = alpha if artist.get_alpha() is None or artist.get_alpha() == 1 else 1
    #     artist.set_alpha(set_this_alpha)

    # elif isinstance(artist, ErrorbarContainer):
    #     children = artist.get_children()
    #     for child in children:
    #         set_this_alpha: float = alpha if child.get_alpha() is None or child.get_alpha() == 1 else 1
    #         child.set_alpha(set_this_alpha)
    # return set_this_alpha


class DoubleSlider(QtWidgets.QSlider):

    # create our our signal that we can connect to if necessary
    doubleValueChanged = pyqtSignal(float)

    def __init__(self, decimals=2, *args, **kargs):
        super(DoubleSlider, self).__init__(*args, **kargs)
        self._multi = 10**decimals

        self.valueChanged.connect(self.emitDoubleValueChanged)

    def emitDoubleValueChanged(self):
        value = float(super(DoubleSlider, self).value()) / self._multi
        self.doubleValueChanged.emit(value)

    def value(self):
        return float(super(DoubleSlider, self).value()) / self._multi

    def setMinimum(self, value):
        return super(DoubleSlider, self).setMinimum(value * self._multi)

    def setMaximum(self, value):
        return super(DoubleSlider, self).setMaximum(int(value * self._multi))

    def setSingleStep(self, value):
        return super(DoubleSlider, self).setSingleStep(value * self._multi)

    def singleStep(self):
        return float(super(DoubleSlider, self).singleStep()) / self._multi

    def setValue(self, value):
        super(DoubleSlider, self).setValue(int(value * self._multi))
