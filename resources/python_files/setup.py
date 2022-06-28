from setuptools import find_packages, setup

setup(
    name="felionlib",
    packages=find_packages(),
    package_data={"felionpy": ["icons/*"]},
    install_requires=["numpy", "scipy", "uncertainties", "matplotlib", "PyQt6", "flask_cors", "waitress"],
    version="0.1.0",
    description="felionlib: a Python package for the analysis of FELion data",
    author="Aravindh Nivas Marimuthu (FELion, FELIX Labaratory, Nijmegen)",
    license="MIT",
)
