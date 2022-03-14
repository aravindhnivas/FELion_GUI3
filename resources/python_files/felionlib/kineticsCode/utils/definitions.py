import numpy as np

def log(*msg): 
    print(msg, flush=True)

def codeToRun(code):
    exec(code)
    return locals()

def formatArray(arr, precision=2):
    return [np.format_float_scientific(value, precision=precision) for value in arr]