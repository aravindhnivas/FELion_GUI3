import sys
import json
import warnings
import traceback
from time import perf_counter
from importlib import import_module
from tkinter.messagebox import showerror

if __name__ == "__main__":

    try:


        startTime = perf_counter()

        pyfile = sys.argv[1]
        args = None

        if len(sys.argv)>2:
            args = json.loads(sys.argv[2])

        print(f"{pyfile=}\n{args=}", flush=True)

        with warnings.catch_warnings(record=True) as warn:

            warnings.simplefilter("ignore")
            pyfunction = import_module(f"felionlib.{pyfile}")
            
            if args:
                pyfunction.main(args)
            else:
                pyfunction.main()
                
            print(f"{warn=}", flush=True)

        print(f"function execution done in {(perf_counter() - startTime):.2f} s")

    except Exception:
        
        showerror("ERROR", traceback.format_exc(5))
    
    finally:
    
        print("Process closed", flush=True)