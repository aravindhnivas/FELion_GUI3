import felionQt
from importlib import reload
import PyQt6.QtWidgets as Qtwidgets
# from PyQt6.QtCore import Qt, pyqtSignal
# import numpy as np
# Qtwidgets = felionQt.QtWidgets

def main():

    widget: felionQt.felionQtWindow = reload(felionQt).felionQtWindow(
        title="Sliders-demo", createControlLayout=False
    )

    widgetGroupLayout = Qtwidgets.QVBoxLayout()

    slider1_layout, slider1 = widget.makeSlider("S1", 0.5, _max=0.5*5)
    
    widgetGroupLayout.addLayout(slider1_layout)

    widget.createControlLayout(optimize=True, attachControlLayout=False)
    widget.controlLayout.addLayout(widgetGroupLayout)
    
    widget.attachControlLayout()
    widget.toggle_controller_layout()
    # slider1: Qtwidgets.QSlider = widget.findChild(Qtwidgets.QSlider, name="slider_S1")
    print("finding slider from layout: ", slider1)
    # slider1.setTickInterval(1.5)
