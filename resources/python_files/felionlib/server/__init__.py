from .flask import app
from gevent.pywsgi import WSGIServer

def main(args):
    
    PORT = int(args["port"])
    DEBUG = int(args["debug"])
    
    if DEBUG:
        app.run(port=PORT, debug=True)
        print("Server running in debug mode", flush=True)
        return

    http_server = WSGIServer(('', PORT), app)
    http_server.serve_forever()
    print("Server running", http_server, flush=True)