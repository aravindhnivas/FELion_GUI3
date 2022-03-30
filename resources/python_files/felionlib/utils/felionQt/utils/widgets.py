import PyQt6.QtWidgets as QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from pathlib import Path as pt
from matplotlib.artist import Artist
from matplotlib.container import Container
from typing import Union


filepath = pt(__file__).parent.resolve()
iconfile = filepath / "../icons/icon.ico"


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
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
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


def toggle_this_artist(artist: Union[Container, Artist], alpha: float) -> float:

    if not (isinstance(artist, Artist) or isinstance(artist, Container)):
        return print(f"unknown toggle method for this artist type\n{type(artist)=}\{artist=}", flush=True)
    set_this_alpha = alpha
    if isinstance(artist, Artist):
        set_this_alpha: float = alpha if artist.get_alpha() is None or artist.get_alpha() == 1 else 1
        artist.set_alpha(set_this_alpha)
    elif isinstance(artist, Container):
        for child in artist.get_children():
            set_this_alpha: float = alpha if child.get_alpha() is None or child.get_alpha() == 1 else 1
            child.set_alpha(set_this_alpha)
    return set_this_alpha
