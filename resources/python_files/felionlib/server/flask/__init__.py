import json
import warnings
import traceback
from time import perf_counter
from importlib import import_module, reload
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from pathlib import Path as pt
import os

# from multiprocessing import Process
app = Flask(__name__)
CORS(app)


def logger(*args, **kwargs):
    print(*args, **kwargs, flush=True)


@app.route("/")
def home():
    return "Server running: felionpy"


@app.errorhandler(404)
def pyError(error):
    return jsonify(error=str(error)), 404


save_location = pt(os.getenv("TEMP")) / "FELion_GUI3"


@app.route("/", methods=["POST"])
def compute():

    logger("fetching request")

    try:

        startTime = perf_counter()
        data = request.get_json()
        pyfile = data["pyfile"]

        calling_file = pyfile.split(".")[-1]
        filename = save_location / f"{calling_file}_data.json"
        args = data["args"]

        logger(f"{pyfile=}\n{args=}")

        with warnings.catch_warnings(record=True) as warn:
            pyfunction = import_module(f"felionlib.{pyfile}")
            pyfunction = reload(pyfunction)
            output = pyfunction.main(args)
            logger(f"{warn=}")

        timeConsumed = perf_counter() - startTime
        logger(f"function execution done in {timeConsumed:.2f} s")
        
        if isinstance(output, dict):
            logger(f"Returning received to client")
            return jsonify(output)

        if not filename.exists():
            raise Exception("Computed file is neither returned from main function or saved to temperary location")
                    
        with open(filename, "r") as f:
            data = json.load(f)
        return jsonify(data)

    except Exception:
        
        error = traceback.format_exc(5)
        logger("catching the error occured in python", error)
        abort(404, description=error)
        