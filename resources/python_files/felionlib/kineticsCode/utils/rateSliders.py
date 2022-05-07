import numpy as np

from .sliderlog import Sliderlog
from .configfile import ratek3, ratekCID, keyFoundForRate
from felionlib.kineticsCode import widget, k3Labels, kCIDLabels


k3Sliders = {}
kCIDSliders = {}


def update_sliders(k3_fit: list[float], kCID_fit: list[float]):

    global k3Sliders, kCIDSliders

    try:
        for counter0, _k3 in enumerate(k3Sliders.values()):
            _k3.set_val(np.log10(k3_fit[counter0]))

        for counter1, _kCID in enumerate(kCIDSliders.values()):
            _kCID.set_val(np.log10(kCID_fit[counter1]))

        print("sliders updated", flush=True)
    except Exception as err:
        print(f"error updating sliders: {err}", flush=True)


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

        valmin = -31
        valmax = -28
        valstep = 1e-6

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

        valmin = -18
        valmax = -12
        valstep = 1e-6

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
