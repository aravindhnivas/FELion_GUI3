
from .flask import app
from importlib import reload
from gevent.pywsgi import WSGIServer

def main(args):
    PORT = int(args["port"])
    http_server = WSGIServer(('', PORT), app)
    http_server.serve_forever()
    print("Server running", http_server, flush=True)