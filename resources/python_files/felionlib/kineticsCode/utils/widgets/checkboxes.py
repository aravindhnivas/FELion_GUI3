# from typing import Callable
from felionlib.utils.felionQt import QtWidgets
from felionlib.utils import logger
# from felionlib.kineticsCode.utils.definitions import codeToRun
# import ctypes

checkboxes = {
    "set_bound": False,
    "include_error": True
}

def codeToRun(code):
    
    exec(code)
    return locals()

def update_checkboxes(key: str, value: bool):
    
    global checkboxes
    value = bool(value)
    # logger("setting: ", key, value)
    checkboxes[key] = value
    # logger(f"{checkboxes=}")

global_key_reference = 'set_bound'


def makeCheckboxes() -> list[QtWidgets.QCheckBox]:
    
    checkbox_widgets_collections: list[QtWidgets.QCheckBox] = []
    for key, value in checkboxes.items():
        logger("added: ", key, value)
        
        current_widget = QtWidgets.QCheckBox(key)
        current_widget.setChecked(value)
        
        code = f"def callback(value: bool):\n\tupdate_checkboxes('{key}', value)"
        codeOutput = codeToRun(code)
        
        callback = codeOutput['callback']
        logger("callback: ", callback)
        current_widget.stateChanged.connect(callback)

        checkbox_widgets_collections += [current_widget]

    return checkbox_widgets_collections

def attach_checkboxes(ncols=3) -> QtWidgets.QVBoxLayout:
    
    checkbox_widgets_collections = makeCheckboxes()
    
    layouts_container = QtWidgets.QVBoxLayout()
    layouts: list[QtWidgets.QHBoxLayout] = [QtWidgets.QHBoxLayout()]
    
    row_items_counter = 1

    for checkbox_widget in checkbox_widgets_collections:

        if row_items_counter <= ncols:
            layouts[-1].addWidget(checkbox_widget)
            row_items_counter += 1

        if row_items_counter > ncols:           
            layouts += [QtWidgets.QHBoxLayout()]
            row_items_counter = 1
            
    for layout in layouts:
        layouts_container.addLayout(layout)

    return layouts_container

