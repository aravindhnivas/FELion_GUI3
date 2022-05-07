import numpy as np
# import traceback
from .sliderlog import Sliderlog
from .configfile import ratek3, ratekCID, keyFoundForRate
from felionlib.kineticsCode import widget, k3Labels, kCIDLabels, widget


k3Sliders: dict[str, Sliderlog] = {}
kCIDSliders: dict[str, Sliderlog] = {}
k3_min_max_step = (-33, -25, 1e-6)
kCID_min_max_step = (-20, -10, 1e-6)


def safe_update_sliders(Sliders: dict[str, Sliderlog], values: list[float], min_max_step: list[float]):
    
    try:
        for slider, received_val in zip(Sliders.values(), values):
            converted_val = np.log10(received_val)
            if np.isnan(converted_val):
                converted_val = min_max_step[0]
            slider.set_val(converted_val)
    
    except Exception:
        # tb = traceback.format_exc(limit=5)
        widget.showErrorDialog(title="Error while updating sliders")
        
def update_sliders(k3_fit: list[float], kCID_fit: list[float]):
    safe_update_sliders(k3Sliders, k3_fit, k3_min_max_step)
    safe_update_sliders(kCIDSliders, kCID_fit, kCID_min_max_step)
    print("sliders updated", flush=True)

def make_slider():

    global k3Sliders, kCIDSliders
    from .fit import update, kvalueLimits

    widget.ax.margins(x=0)

    height = 0.03
    width = 0.25
    bottom = 0.9

    counter = 0

    k3SliderAxes = []

    for label in k3Labels:

        axes = [0.65, bottom, width, height]
        current_k3SliderAxes = widget.fig.add_axes(axes)

        if counter + 1 <= min(len(ratek3), len(ratekCID)):
            current_k3SliderAxes.patch.set_facecolor(f"C{counter+1}")
            current_k3SliderAxes.patch.set_alpha(0.7)

        # valmin = -33
        # valmax = -25
        # valstep = 1e-6
        valmin, valmax, valstep = k3_min_max_step
        if label in kvalueLimits:
            valmin, valmax, valinit = kvalueLimits[label]

            if keyFoundForRate:
                valinit = np.log10(ratek3[counter])

        else:
            valinit = np.log10(ratek3[counter])

        # print(valmin, valmax, valinit, flush=True)

        _k3Slider = Sliderlog(
            ax=current_k3SliderAxes,
            label=label,
            valstep=valstep,
            valfmt="%.2e",
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

    for label in kCIDLabels:
        axes = [0.65, bottom, width, height]
        current_kCIDSliderAxes = widget.fig.add_axes(axes)

        if counter + 1 <= min(len(ratek3), len(ratekCID)):

            current_kCIDSliderAxes.patch.set_facecolor(f"C{counter+1}")
            current_kCIDSliderAxes.patch.set_alpha(0.7)

        # valmin = -20
        # valmax = -10
        # valstep = 1e-6
        valmin, valmax, valstep = kCID_min_max_step
        if label in kvalueLimits:

            valmin, valmax, valinit = kvalueLimits[label]
        else:
            valinit = np.log10(ratekCID[counter])

        _kCIDSlider = Sliderlog(
            ax=current_kCIDSliderAxes,
            label=label,
            valstep=valstep,
            valfmt="%.2e",
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
