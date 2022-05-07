from felionlib.utils.felionQt import QtWidgets
from .widgets.checkboxes import attach_checkboxes


def make_widgets():
    
    from felionlib.kineticsCode import (
        widget, kinetic_plot_adjust_configs_obj
    )
    
    from felionlib.kineticsCode.utils.fit import fit_kinetic_data
    from .savedata import saveData
    
    additional_widgets_group = QtWidgets.QGroupBox()
    additional_widgets_layout = QtWidgets.QVBoxLayout()

    buttons_layout0 = QtWidgets.QHBoxLayout()
    toggle_slider_widgets = QtWidgets.QPushButton("Toggle sliders visibility")

    def hideSliderWidgets():
        
        state = widget.sliderWidgets[0].get_visible()
        
        for slider_widget in widget.sliderWidgets:
            slider_widget.set_visible(not state)
        widget.draw()

    toggle_slider_widgets.clicked.connect(hideSliderWidgets)
    
    subplot_adjust_button = QtWidgets.QPushButton("Restore subplots")
    subplot_adjust_button.clicked.connect(lambda: (widget.fig.subplots_adjust(**kinetic_plot_adjust_configs_obj), widget.draw()))

    buttons_layout0.addWidget(toggle_slider_widgets)
    buttons_layout0.addWidget(subplot_adjust_button)

    fit_button = QtWidgets.QPushButton("Fit")
    # fit_button.clicked.connect(fitfunc)
    fit_button.clicked.connect(fit_kinetic_data)

    saveData_button = QtWidgets.QPushButton("saveData")
    saveData_button.clicked.connect(saveData)

    buttons1_layout = QtWidgets.QHBoxLayout()
    buttons1_layout.addWidget(fit_button)
    buttons1_layout.addWidget(saveData_button)
    
    buttons1_layout = QtWidgets.QHBoxLayout()
    buttons1_layout.addWidget(fit_button)
    buttons1_layout.addWidget(saveData_button)
    
    additional_widgets_layout.addLayout(buttons_layout0)
    additional_widgets_layout.addLayout(buttons1_layout)
    
    checkboxes_layout = attach_checkboxes()
    additional_widgets_layout.addLayout(checkboxes_layout)
    
    additional_widgets_group.setLayout(additional_widgets_layout)
    widget.finalControlLayout.addWidget(additional_widgets_group)
    
    widget.attachControlLayout()
    