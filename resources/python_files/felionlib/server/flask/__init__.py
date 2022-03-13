import warnings
from time import perf_counter
from importlib import import_module, reload
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app)

@app.route('/')
def home():
    return "Server running: felionpy"

@app.route('/', methods=["POST"])
def compute():
    
    startTime = perf_counter()
    data = request.get_json()
    pyfile = data["pyfile"]
    args = data["args"]

    print(f"{pyfile=}\n{args=}", flush=True)

    with warnings.catch_warnings(record=True) as warn:
        
        warnings.simplefilter("ignore")
        pyfunction = reload(import_module(f"felionlib.{pyfile}"))
        pyfunction.main(args)
        print(f"{warn=}", flush=True)

    timeConsumed = perf_counter() - startTime
    print(f"function execution done in {timeConsumed:.2f} s")
    print(f"###########\n{dir()=}###########\n", flush=True)

    data = jsonify({"timeConsumed": f"{timeConsumed:.2f}"})
    return data
