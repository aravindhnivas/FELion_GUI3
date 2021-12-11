import sys
from time import perf_counter
import json
from importlib import import_module

if __name__ == "__main__":

    startTime = perf_counter()
    
    pyfile = sys.argv[1]
    args = json.loads(sys.argv[2])
    print(f"{pyfile=}\n{args=}", flush=True)

    pyfunction = import_module(pyfile)
    pyfunction.main(args)
    print(f"function execution done in {(perf_counter() - startTime):.2f} s")
