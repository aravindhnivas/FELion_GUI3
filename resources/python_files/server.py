import warnings
import os
import json
from flask_cors import CORS
from flask import Flask, request, jsonify
from time import perf_counter
from importlib import import_module
from pathlib import Path as pt

PORT = 5050
app = Flask(__name__)
cors = CORS(app)

@app.route('/felionpy/<pyfile>')
def profile(pyfile):
    return f'{pyfile=}'


save_location = pt(os.getenv("TEMP")) / "FELion_GUI3"


@app.route('/felionpy/compute', methods=["POST"])
def postME():

    # data = request.get_json()
    # print(data, type(data))
    # data = jsonify(data)
    # return data
    startTime = perf_counter()
    data = request.get_json()
    pyfile = data["pyfile"]
    args = data["args"]
    print(f"{pyfile=}\n{args=}", flush=True)

    with warnings.catch_warnings(record=True) as warn:
        warnings.simplefilter("ignore")
        pyfunction = import_module(f"felionlib.{pyfile}")
        pyfunction.main(args)
        print(f"{warn=}", flush=True)

    timeConsumed = perf_counter() - startTime
    print(f"function execution done in {timeConsumed:.2f} s")

    data = jsonify({"timeConsumed": f"{timeConsumed:.2f}"})
    return data

if __name__ == "__main__": 
    app.run(port=PORT, debug=True)
