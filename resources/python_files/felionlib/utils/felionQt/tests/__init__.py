
from importlib import import_module, reload
from PyQt6.QtWidgets import QApplication
# from .subplots_play import main as testFunc
def run():
    qapp = QApplication.instance()
    if not qapp:
        qapp = QApplication([])
    reload(import_module("felionQt.tests.subplots_play")).main()
    # testFunc()
    qapp.exec()