from typing import Literal
import numpy as np
from scipy.optimize import curve_fit
from scipy.integrate import solve_ivp
from felionlib.utils import logger

from felionlib.kineticsCode.utils.plot import fitPlot
from felionlib.kineticsCode import (
    expTime,
    expData,
    expDataError,
    widget,
    initialValues,
    tspan,
    simulateTime,
    kinetics_equation_file,
    # numberDensity
)
from felionlib.kineticsCode.utils.widgets.checkboxes import checkboxes
from .configfile import ratek3, ratekCID, k_err as k_err_config

from felionlib.utils.FELion_definitions import readCodeFromFile
from felionlib.kineticsCode.utils.rateSliders import k3Sliders, kCIDSliders, update_sliders
from .plotWidgets import fitStatus_label_widget, fit_methods_widget, solve_ivp_methods_widget, bounds_percent_widget

k_err = k_err_config
rateCoefficientArgs: tuple[list[float], list[float]] = (ratek3, ratekCID)
k_fit: np.ndarray = None


fit_method = "lm"
solve_ivp_method = "Radau"


def update_fit_method(val: str = None):
    global fit_method
    fit_method = val
    print(f"{fit_method=}", flush=True)


fit_methods_widget.currentTextChanged.connect(update_fit_method)


def update_solve_ivp_method(val: str = None):
    global solve_ivp_method
    solve_ivp_method = val
    print(f"{solve_ivp_method=}", flush=True)


solve_ivp_methods_widget.currentTextChanged.connect(update_solve_ivp_method)

bounds_percent = 10


def update_bounds_percent(val: int = None):
    global bounds_percent
    bounds_percent = val


bounds_percent_widget.valueChanged.connect(update_bounds_percent)


def codeToRun(code: str):
    exec(code)
    return locals()


codeContents = readCodeFromFile(kinetics_equation_file)
codeOutput = codeToRun(codeContents)
compute_attachment_process = codeOutput["compute_attachment_process"]


def intialize_fit_plot() -> None:
    results = solve_ivp(
        compute_attachment_process,
        tspan,
        initialValues,
        method=solve_ivp_method,
        t_eval=simulateTime,
    )

    dNdtSol = results.y
    return dNdtSol


def update(val: float = None):

    global rateCoefficientArgs

    try:
        rateCoefficientArgs = (
            [rate.val for rate in k3Sliders.values()],
            [rate.val for rate in kCIDSliders.values()],
        )
        dNdtSol = solve_ivp(
            compute_attachment_process, tspan, initialValues, method=solve_ivp_method, t_eval=simulateTime
        ).y

        for line, fitted_data in zip(fitPlot, dNdtSol):
            line.set_ydata(fitted_data)
        fitted_sum = dNdtSol.sum(axis=0)
        fitPlot[-1].set_ydata(fitted_sum)
        widget.blit.update()

    except Exception:
        widget.showErrorDialog()


def fitODE(t: np.ndarray, *args):

    global rateCoefficientArgs

    tspan = [0, t.max() * 1.2]
    rateCoefficientArgs = (args[: len(ratek3)], args[len(ratek3) :])

    if not np.all(np.isfinite(args)):
        raise ValueError("NaN or Inf in rateCoefficientArgs")
    dNdtSol: np.ndarray = solve_ivp(
        compute_attachment_process, tspan, initialValues, method=solve_ivp_method, t_eval=t
    ).y
    return dNdtSol.flatten()


def fit_kinetic_data() -> None:
    global k_fit, k_err, rateCoefficientArgs

    fitStatus_label_widget.setText("Fitting...")
    setbound = checkboxes["set_bound"]
    includeError = checkboxes["include_error"]
    p0 = np.array([*[rate.val for rate in k3Sliders.values()], *[rate.val for rate in kCIDSliders.values()]])
    p0 = np.nan_to_num(p0).clip(min=0)
    bounds = (-np.inf, np.inf)

    if setbound:
        # percent = 10
        bounds = (
            [
                *[rate.val - (bounds_percent / 100) * rate.val for rate in k3Sliders.values()],
                *[rate.val - (bounds_percent / 100) * rate.val for rate in kCIDSliders.values()],
            ],
            [
                *[rate.val + (bounds_percent / 100) * rate.val for rate in k3Sliders.values()],
                *[rate.val + (bounds_percent / 100) * rate.val for rate in kCIDSliders.values()],
            ],
        )
    logger(f"{bounds=}")
    try:

        print(f"fitting using method: {fit_method=} ", flush=True)
        k_fit, kcov = curve_fit(
            fitODE,
            expTime,
            expData.flatten(),
            p0=p0,
            bounds=bounds,
            sigma=expDataError.flatten() if includeError else None,
            absolute_sigma=includeError,
            method=fit_method,
        )
        k_err = np.sqrt(np.diag(kcov))
        logger(f"{k_fit=}\n{k_err=}")
        logger("fitted")
        k3_fit = k_fit[: len(ratek3)]
        kCID_fit = k_fit[len(ratek3) :]
        update_sliders(k3_fit, kCID_fit)

        # rateCoefficientArgs = (k3_fit, kCID_fit)

        if not np.all(np.isfinite(k_fit)):
            raise ValueError("Fitted values are not finite")

        if not np.all(np.isfinite(k_err)):
            widget.showdialog(
                "Warning", "Non-finite error values\nTry fitting with higher different timeStartIndex", "warning"
            )
            fitStatus_label_widget.setText("Non-finite error values")

        fitStatus_label_widget.setText("Fitted")

    except Exception as err:
        print(f"error: {err}")
        widget.showErrorDialog()
        fitStatus_label_widget.setText("Failed")
