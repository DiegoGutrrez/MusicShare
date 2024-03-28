import contextlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from urllib.parse import urlparse, parse_qs
import threading

class SuppressedLogHTTPRequestHandler(BaseHTTPRequestHandler):
    def log_request(self, code='-', size='-'):
        pass

class RequestHandlerUserAuth(SuppressedLogHTTPRequestHandler):
    def do_GET(self):
        global authorization_code, state
        # Obtener la ruta de la solicitud
        path = urlparse(self.path)
        
        # Obtener los parámetros de la consulta
        query_parameters = parse_qs(path.query)

        # Obtener los valores de los parámetros de la consulta
        authorization_code = query_parameters.get('code', [None])[0]
        state = query_parameters.get('state', [None])[0]

        # Responder con un mensaje de éxito
        self.send_response(200)
        self.send_header('Content-type', 'text/html') 
        self.end_headers()
        message = "<h1>PUEDES CERRAR EL NAVEGADOR</h1>".encode("utf-8")
        self.wfile.write(message)





def StartWebServerUserAuth(PORT):
    global authorization_code, state
    authorization_code = None
    state = None
    server = HTTPServer(('localhost', PORT), RequestHandlerUserAuth)

    
    server.handle_request()
    # server.handle_request()

    # def serve():
    #     server.handle_request()
    #     return

    # # Crear un hilo para manejar las solicitudes
    # threading.Thread(target=serve).start()

    # # Esperar a que lleguen las solicitudes
    # while authorization_code is None or state is None:
    #     pass

    return authorization_code, state

