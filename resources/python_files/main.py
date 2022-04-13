import sys
import json
import warnings
from importlib import import_module


if __name__ == "__main__":

    pyfile = sys.argv[1]
    args = None
    if len(sys.argv)>2:
        args = json.loads(sys.argv[2])

    print(f"{pyfile=}\n{args=}", flush=True)
    with warnings.catch_warnings(record=True) as warn:
        pyfunction = import_module(f"felionlib.{pyfile}")
        if args:
            pyfunction.main(args)
        else:
            pyfunction.main()
            