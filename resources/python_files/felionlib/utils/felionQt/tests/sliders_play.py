import felionQt
from importlib import reload
import PyQt6.QtWidgets as Qtwidgets
from PyQt6.QtCore import Qt
import numpy as np

def main():
    widget: felionQt.felionQtWindow = reload(felionQt).felionQtWindow(
        title="Sliders-demo", makeControlLayout=False
    )

    widgetGroupLayout = Qtwidgets.QVBoxLayout()

    values = np.array([12, 25, 16])
    normalised_values = (values - values.min()) / (values.max() - values.min()) * 100

    slider1_range = (12, 25)
    slider1_values = np.linspace(12, 25, 100)

    def slider1_callback(val: int):
        # nonlocal slider1_trailing_label
        slider1_real_value = round(slider1_values[val], 2)
        slider1_trailing_label.setText(f"{str(slider1_real_value)}")
        # print(val)
    
    slider1_widget, _ = widget.makeSlider("S1", callback=slider1_callback)
    slider1_trailing_label = Qtwidgets.QLabel("0")
    
    slider1_widget.addWidget(slider1_trailing_label)
    slider2, *_ = widget.makeSlider("S2")

    widgetGroupLayout.addLayout(slider1_widget)
    widgetGroupLayout.addLayout(slider2)

    widget.createControlLayout(optimize=True)
    widget.controlLayout.addLayout(widgetGroupLayout)

    print(f"{widget.controlLayout.objectName()=}")

    widget.showWidget()
    widget.toggle_controller_layout()

