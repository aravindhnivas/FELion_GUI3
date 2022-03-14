
import warnings
import traceback
from time import perf_counter
from importlib import import_module, reload
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)



@app.route('/')
def home():
    return "Server running: felionpy"

@app.errorhandler(404)
def pyError(error):
    return jsonify(error=str(error)), 404

@app.route('/', methods=["POST"])
def compute():
    
    try:
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
        data = {"timeConsumed": f"{timeConsumed:.2f} s"}

        return jsonify(data)

    except Exception:
        error = traceback.format_exc(5)
        print("catching the error occured in python", error, flush=True)
        abort(404, description=error)

    finally:
        print("Process closed", flush=True)
