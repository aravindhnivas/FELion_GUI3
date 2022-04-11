import numpy as np
from .sliderlog import Sliderlog


# k3Sliders = {}
# kCIDSliders = {}


def make_slider(widget, k3Labels, kCIDLabels, ratek3, ratekCID, kvalueLimits, keyFoundForRate, update):

    # global k3Sliders, kCIDSliders

    k3Sliders = {}
    kCIDSliders = {}

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

        valmin = -33
        valmax = -25
        valstep = 1e-4

        if label in kvalueLimits:
            valmin, valmax, valinit = kvalueLimits[label]

            if keyFoundForRate:
                valinit = np.log10(ratek3[counter])

        else:
            valinit = np.log10(ratek3[counter])

        print(valmin, valmax, valinit, flush=True)

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

        valmin = -20
        valmax = -10
        valstep = 1e-4

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
