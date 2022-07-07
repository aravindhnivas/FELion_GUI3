import felionlib
from pathlib import Path as pt

hiddenimports = [
    "felionlib.getVersion",
    "felionlib.depletionscan",
    "felionlib.timescan",
    "felionlib.thz_scan",
    "felionlib.utils",
    "felionlib.mass",
    "felionlib.server",
    "felionlib.kineticsCode",
    "felionlib.normline",
    "felionlib.ROSAA",
    "felionlib.numberDensity",
    "felionlib.THz",
]
icons_path = pt(felionlib.__file__).parent / "../icons/*"
icons_path = icons_path.resolve().__str__()
datas = [(icons_path, "icons")]
