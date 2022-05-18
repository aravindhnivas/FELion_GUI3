from uncertainties import ufloat
from scipy.constants import Boltzmann as kB


def main(args):
    def get_data_with_uncertainties(key, percentage=False):
        value, err = [float(i) for i in args[key]]

        if not percentage:
            return ufloat(value, err)
        err_percent = err / 100 * value
        return ufloat(value, err_percent)

    background_pressure = get_data_with_uncertainties("background_pressure")
    added_pressure = get_data_with_uncertainties("added_pressure")
    trap_temperature = get_data_with_uncertainties("trap_temperature")

    srgMode = bool(args["srgMode"])
    if srgMode:
        calibration_factor = 1
    else:
        calibration_factor = get_data_with_uncertainties("calibration_factor")
    room_temperature = get_data_with_uncertainties("room_temperature")

    changeInPressure = added_pressure - background_pressure
    pressure_srg = calibration_factor * changeInPressure

    print(f"{background_pressure=:.2e}", flush=True)
    print(f"{added_pressure=:.2e}", flush=True)
    print(f"{changeInPressure=:.2e}", flush=True)
    print(f"{trap_temperature=:.2e}", flush=True)

    kB_in_cm = kB * 1e4

    constant_factor = 1 / (kB_in_cm * room_temperature**0.5)
    print(f"{constant_factor=:.2e}", flush=True)
    nHe = constant_factor * pressure_srg / trap_temperature**0.5
    print(f"{nHe=:.2e}", flush=True)

    # Takaishi-Sensui equation
    TakasuiSensuiConstants = args["TakasuiSensuiConstants"]
    tube_diameter = float(args["tube_diameter"])
    X = (2 * pressure_srg * 100 * tube_diameter) / (trap_temperature + room_temperature)  # mm. Pa. / K
    A = float(TakasuiSensuiConstants["A"])
    B = float(TakasuiSensuiConstants["B"])
    C = float(TakasuiSensuiConstants["C"])

    numerator = (trap_temperature / room_temperature) ** 0.5 - 1
    denomiator = A * X**2 + B * X + C * X**0.5 + 1
    pressure_trap_by_srg = 1 + (numerator / denomiator)

    F = (1 - pressure_trap_by_srg) / (1 - (trap_temperature / room_temperature) ** 0.5)
    pressure_trap = pressure_srg * pressure_trap_by_srg

    nHe_transpiration = pressure_trap / (kB_in_cm * trap_temperature)
    print(f"{nHe_transpiration=:.2e}", flush=True)
    print(f"{X=:.3e}\t{F=:.3e}", flush=True)

    send_data = {"nHe": f"{nHe:.3e}", "nHe_transpiration": f"{nHe_transpiration:.3e}", "X": f"{X:.3e}", "F": f"{F:.3e}"}
    return send_data
