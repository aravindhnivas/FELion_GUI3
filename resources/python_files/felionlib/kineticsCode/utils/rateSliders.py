import numpy as np
from matplotlib.widgets import Slider

from felionlib.kineticsCode import widget


k3Sliders: dict[str, Slider] = {}
kCIDSliders: dict[str, Slider] = {}


def safe_update_sliders(Sliders: dict[str, Slider], values: list[float]):

    try:
        for slider, value in zip(Sliders.values(), values):
            if np.isnan(value):
                value = 0
            slider.set_val(value)
    except Exception:
        widget.showErrorDialog(title="Error while updating sliders")


def update_sliders(k3_fit: list[float], kCID_fit: list[float]):
    safe_update_sliders(k3Sliders, k3_fit)
    safe_update_sliders(kCIDSliders, kCID_fit)
    print("sliders updated", flush=True)


def make_slider():

    global k3Sliders, kCIDSliders

    from .fit import update, min_max_step_controller
    from .configfile import ratek3, ratekCID

    # print(f"{ratek3=}\n{ratekCID=}", flush=True)
    widget.ax.margins(x=0)

    height = 0.03
    width = 0.25
    bottom = 0.9

    counter = 0

    k3SliderAxes = []

    k3Labels = min_max_step_controller["forwards"]
    kCIDLabels = min_max_step_controller["backwards"]
    # return print(f"{k3Labels.values()=}")

    for label, controller in k3Labels.items():

        axes = [0.65, bottom, width, height]
        current_k3SliderAxes = widget.fig.add_axes(axes)
        valmin, valmax, valstep = controller
        valinit = ratek3[counter]
        _k3Slider = Slider(
            ax=current_k3SliderAxes,
            label=label,
            valstep=valstep,
            valfmt="%.4f",
            valmin=valmin,
            valmax=valmax,
            valinit=valinit,
        )

        _k3Slider.on_changed(update)
        k3Sliders[label] = _k3Slider
        bottom -= height * 1.6
        counter += 1
        k3SliderAxes.append(current_k3SliderAxes)

    bottom -= height * 2

    counter = 0
    kCIDSliderAxes = []

    for label, controller in kCIDLabels.items():
        axes = [0.65, bottom, width, height]
        current_kCIDSliderAxes = widget.fig.add_axes(axes)

        if counter + 1 <= min(len(ratek3), len(ratekCID)):

            current_kCIDSliderAxes.patch.set_facecolor(f"C{counter+1}")
            current_kCIDSliderAxes.patch.set_alpha(0.7)

        valmin, valmax, valstep = controller
        valinit = ratekCID[counter]
        _kCIDSlider = Slider(
            ax=current_kCIDSliderAxes,
            label=label,
            valstep=valstep,
            valfmt="%.4f",
            valmin=valmin,
            valmax=valmax,
            valinit=valinit,
        )

        _kCIDSlider.on_changed(update)
        kCIDSliders[label] = _kCIDSlider

        bottom -= height * 1.6
        counter += 1
        kCIDSliderAxes.append(current_kCIDSliderAxes)

    widget.sliderWidgets = k3SliderAxes + kCIDSliderAxes

    return k3Sliders, kCIDSliders
