import sys
import json
import warnings
from time import perf_counter
from importlib import import_module

if __name__ == "__main__":

    startTime = perf_counter()
    print(f"{sys.argv=}")
    pyfile = sys.argv[1]
    args = json.loads(sys.argv[2])

    print(f"{pyfile=}\n{args=}", flush=True)

    with warnings.catch_warnings(record=True) as warn:
        warnings.simplefilter("ignore")
        pyfunction = import_module(f"felionlib.{pyfile}")
        pyfunction.main(args)
        print(f"{warn=}", flush=True)

    print(f"function execution done in {(perf_counter() - startTime):.2f} s")
