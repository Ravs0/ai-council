from http.server import HTTPServer
from api.call import handler
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

class RequestHandler(handler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

def run(server_class=HTTPServer, handler_class=RequestHandler, port=3000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting API server on port {port}...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == "__main__":
    run()
