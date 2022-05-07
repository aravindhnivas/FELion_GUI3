import sys
import json
import warnings
from importlib import import_module
# import traceback
# import ctypes

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

# def excepthook(etype, value, tb):
#     tb = "".join(traceback.format_exception(etype, value, tb, limit=5))
#     print("error catched!:", value, flush=True)
#     print("error message:\n", tb, flush=True)
    
#     MB_ICONERROR = 0x10
#     ctypes.windll.user32.MessageBoxW(None, tb, etype.__name__, MB_ICONERROR)
#     return
    
# sys.excepthook = excepthook
