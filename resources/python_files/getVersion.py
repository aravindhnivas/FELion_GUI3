import sys

def main(args):
    print("Function starting")
    version_info = sys.version_info
    version = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    print(f"Python {version}")