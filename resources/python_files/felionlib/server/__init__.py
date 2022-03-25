from .flask import app
import waitress

def main(args):
    PORT = int(args["port"])
    DEBUG = int(args["debug"])
    if DEBUG:
        app.run(port=PORT, debug=True)
        print("Server running in debug mode", flush=True)
        return
    waitress.serve(app, port=PORT, url_scheme='http')
    