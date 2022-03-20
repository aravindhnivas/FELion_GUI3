# from .savedata import saveData

widget = None
# numberDensity = None
# checkboxes = {
#     "setbound": False
# }

def checkboxesFunc(event=None):
    global setbound
    print(f"{setbound.get()=}", flush=True)
    checkboxes["setbound"] = not setbound.get()


# def setNumberDensity(val):
#     global numberDensity
#     numberDensity = float(val)
#     print(f"{numberDensity=}", flush=True)
#     fitfunc()


def make_widgets(**kwargs):

    global widget, fitfunc, setbound, checkboxes

    widget = kwargs["widget"]
    fitfunc = kwargs["fitfunc"]
    checkboxes = kwargs["checkboxes"]
    # saveDataArgs = kwargs["saveDataArgs"]
    saveData = kwargs["saveData"]

    widget.last_y = widget.last_y + widget.y_diff
    setbound = widget.Entries(
        "Check", "setbound", widget.x0, widget.last_y, 
        default=checkboxes["setbound"], bind_btn=True, 
        bind_func=checkboxesFunc
    )

    widget.Buttons(
        "Fit", widget.x0+widget.x_diff, widget.last_y,
        fitfunc, relwidth=0.4
    )
    
    widget.last_y = widget.last_y + widget.y_diff
    widget.Buttons(
        "saveData", widget.x0, widget.last_y,
        saveData, relwidth=0.4
    )

    return checkboxes