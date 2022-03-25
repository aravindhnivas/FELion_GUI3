from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QIcon
from pathlib import Path as pt


filepath = pt(__file__).parent.resolve()
iconfile = filepath / "../icons/icon.ico"


class ShowDialog(QDialog):

    def __init__(self, title="Info", info="", type="info", parent=None):

        super().__init__(parent)
        dialogBox = QMessageBox(self)
        self.setWindowIcon(QIcon(iconfile.resolve().__str__()))
        
        dialogBox.setWindowTitle(title)
        dialogBox.setText(info)
        
        if type == "info":
            dialogBox.setIcon(QMessageBox.Icon.Information)

        elif type == "warning":
            dialogBox.setIcon(QMessageBox.Icon.Warning)
        
        elif type == "critical":
            dialogBox.setIcon(QMessageBox.Icon.Critical)

        dialogBox.exec()

