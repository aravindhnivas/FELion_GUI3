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
]
icons_path = pt(felionlib.__file__).parent / "../icons/*"
datas = [(icons_path.resolve().__str__(), "icons")]
