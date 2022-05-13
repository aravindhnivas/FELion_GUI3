from felionlib.utils.felionQt import QtWidgets, Qt
from .widgets.checkboxes import attach_checkboxes

# from felionlib.kineticsCode import widget


fitStatus_label_widget = QtWidgets.QLabel("")
fit_methods_widget = QtWidgets.QComboBox()
solve_ivp_methods_widget = QtWidgets.QComboBox()
# bounds_percent_layout, bounds_percent_widget = widget.makeSlider("bounds(%)", 10, 1, 500)


def make_widgets():

    from felionlib.kineticsCode import widget, kinetic_plot_adjust_configs_obj
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
    subplot_adjust_button.clicked.connect(
        lambda: (widget.fig.subplots_adjust(**kinetic_plot_adjust_configs_obj), widget.draw())
    )

    buttons_layout0.addWidget(toggle_slider_widgets)
    buttons_layout0.addWidget(subplot_adjust_button)

    buttons1_layout = QtWidgets.QHBoxLayout()

    fit_methods_widget.addItems(["lm", "trf", "dogbox"])
    fit_methods_widget.setCurrentText("lm")
    fit_methods_widget.setToolTip("Choose fitting method")

    solve_ivp_methods_widget.addItems(["Radau", "BDF", "RK45", "RK23", "RK12", "DOP853"])
    solve_ivp_methods_widget.setCurrentText("Radau")
    solve_ivp_methods_widget.setToolTip("Choose solve_ivp method")

    buttons1_layout.addWidget(solve_ivp_methods_widget)
    buttons1_layout.addWidget(fit_methods_widget)

    buttons2_layout = QtWidgets.QHBoxLayout()

    fit_button = QtWidgets.QPushButton("Fit")
    fit_button.clicked.connect(fit_kinetic_data)

    saveData_button = QtWidgets.QPushButton("saveData")
    saveData_button.clicked.connect(saveData)

    buttons2_layout.addWidget(fit_button)
    buttons2_layout.addWidget(saveData_button)

    additional_widgets_layout.addLayout(buttons_layout0)
    additional_widgets_layout.addLayout(buttons1_layout)
    additional_widgets_layout.addLayout(buttons2_layout)

    # additional_widgets_layout.addLayout(bounds_percent_layout)
    checkboxes_layout = attach_checkboxes()
    additional_widgets_layout.addLayout(checkboxes_layout)
    additional_widgets_layout.addWidget(fitStatus_label_widget)
    additional_widgets_layout.addStretch()
    # additional_widgets_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    additional_widgets_group.setLayout(additional_widgets_layout)
    controllerDock = QtWidgets.QDockWidget("Fitting controller", widget)
    controllerDock.setWidget(additional_widgets_group)
    controllerDock.setMaximumHeight(200)
    # controllerDock.setFloating(True)
    controllerDock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)
    widget.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, controllerDock)
