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
            if slider.valmax < value:
                label = slider.label.get_text()
                warningMsg = f"{label} fitted {value=:.4f} is greater than {slider.valmax=}\nReset the max value to atleast {(value+0.1*value):.1f}"
                widget.showdialog(msg=warningMsg, type="warning")
            slider.set_val(value)

    except Exception:
        widget.showErrorDialog(title="Error while updating sliders")


def update_sliders(k3_fit: list[float], kCID_fit: list[float]):
    safe_update_sliders(k3Sliders, k3_fit)
    safe_update_sliders(kCIDSliders, kCID_fit)


def make_slider():

    global k3Sliders, kCIDSliders

    from .fit import update
    from .configfile import ratek3, ratekCID, forwards_labels_and_bounds, backwards_labels_and_bounds

    widget.ax.margins(x=0)
    height = 0.03
    width = 0.25
    bottom = 0.9
    counter = 0
    k3SliderAxes = []

    for label, controller in forwards_labels_and_bounds.items():

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
        print(f"setting slider value: {label}: {valinit}\n{k3Sliders[label].val}", flush=True)
        k3SliderAxes.append(current_k3SliderAxes)

    bottom -= height * 2

    counter = 0
    kCIDSliderAxes = []

    for label, controller in backwards_labels_and_bounds.items():
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
        print(f"setting slider value: {label}: {valinit}\n{kCIDSliders[label].val}", flush=True)
        kCIDSliderAxes.append(current_kCIDSliderAxes)

    widget.sliderWidgets = k3SliderAxes + kCIDSliderAxes

    return k3Sliders, kCIDSliders
