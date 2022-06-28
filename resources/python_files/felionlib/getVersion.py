import sys
import felionlib


def main(args=""):
    version_info = sys.version_info
    version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    print(f"Python {version} (felionlib {felionlib.__version__})")
