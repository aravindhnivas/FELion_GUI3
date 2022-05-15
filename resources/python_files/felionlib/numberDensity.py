from uncertainties import ufloat
from scipy.constants import Boltzmann as kB


conditions = None


def get_data_with_uncertainties(key):
    value, err_percent = [float(i) for i in conditions[key]["value"]]
    err_percent = err_percent / 100 * value
    return ufloat(value, err_percent)


def main(args):
    global conditions

    conditions = args["conditions"]

    trap_temperature = get_data_with_uncertainties("temperature")
    background_pressure = get_data_with_uncertainties("background_pressure")
    added_pressure = get_data_with_uncertainties("added_pressure")

    pressure_chamber = added_pressure - background_pressure

    calibration_factor, calibration_factor_err = [float(i) for i in args["calibration_factor"]]
    calibration_factor = ufloat(calibration_factor, calibration_factor_err)
    pressure_srg = calibration_factor * pressure_chamber

    room_temperature, room_temperature_err = [float(i) for i in args["room_temperature"]]
    room_temperature = ufloat(room_temperature, room_temperature_err)

    kB_in_cm = kB * 1e4

    constant_factor = 1 / (kB_in_cm * room_temperature**0.5)
    print(f"{constant_factor=:.2e}", flush=True)
    nHe = constant_factor * pressure_srg / trap_temperature**0.5
    print(f"{nHe=:.2e}", flush=True)

    # Takaishi-Sensui equation
    TakasuiSensuiConstants = args["TakasuiSensuiConstants"]
    tube_diameter = ufloat(float(args["tube_diameter"]), 0)
    X = (2 * pressure_srg * tube_diameter) / (trap_temperature + room_temperature)
    A = float(TakasuiSensuiConstants["A"])
    B = float(TakasuiSensuiConstants["B"])
    C = float(TakasuiSensuiConstants["C"])

    numerator = (trap_temperature / room_temperature) ** 0.5 - 1
    denomiator = A * X**2 + B * X + C * X**0.5 + 1
    pressure_trap = pressure_srg * (1 + (numerator / denomiator))

    nHe_transpiration = pressure_trap / (kB_in_cm * trap_temperature)
    print(f"{nHe_transpiration=:.2e}", flush=True)

    send_data = {"nHe": f"{nHe:.2e}", "nHe_transpiration": f"{nHe_transpiration:.2e}"}
    return send_data
