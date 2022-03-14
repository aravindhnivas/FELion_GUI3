def fitfunc(event=None):

    global k_fit, k_err

    p0 = [*[10**rate.val for rate in k3Sliders.values()], *[10**rate.val for rate in kCIDSliders.values()]]

    if checkboxes["setbound"]:
        ratio = 0.1
        bounds=(
            [
                *[np.format_float_scientific(10**(rate.val-ratio), precision=2) for rate in k3Sliders.values()], 
                *[np.format_float_scientific(10**(rate.val-ratio), precision=2) for rate in kCIDSliders.values()]
            ],
            [
                *[np.format_float_scientific(10**(rate.val+ratio), precision=2) for rate in k3Sliders.values()],
                *[np.format_float_scientific(10**(rate.val+ratio), precision=2) for rate in kCIDSliders.values()]
            ]
        )
    else:
        bounds=([*[1e-33]*len(ratek3), *[1e-17]*len(ratekCID)], [*[1e-29]*len(ratek3), *[1e-14]*len(ratekCID)])
    
    log(f"{bounds=}")
    try:
        k_fit, kcov = curve_fit(fitODE, expTime, expData.flatten(),
            p0=p0, sigma=expDataError.flatten(), absolute_sigma=True, bounds=bounds   
        )

        k_err = np.sqrt(np.diag(kcov))
        log(f"{k_fit=}\n{k_err=}")
        log("fitted")
        
        for counter0, _k3 in enumerate(k3Sliders.values()):
            _k3.set_val(np.log10(k_fit[:len(ratek3)][counter0]))
        for counter1, _kCID in enumerate(kCIDSliders.values()):
            _kCID.set_val(np.log10(k_fit[len(ratek3):][counter1]))
    except Exception:
        k_fit = []
        
        k_err = []
        if plotted:
            MsgBox("Error", traceback.format_exc(), MB_ICONERROR)

