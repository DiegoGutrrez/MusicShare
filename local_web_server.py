from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

class RequestHandlerUserAuth(BaseHTTPRequestHandler):
    def do_GET(self):
        global authorization_code, state
        # Obtener la ruta de la solicitud
        path = urlparse(self.path)
        
        # Obtener los parámetros de la consulta
        query_parameters = parse_qs(path.query)


        # Obtener los valores de los parámetros de la consulta
        authorization_code = query_parameters.get('code', [None])[0]
        state = query_parameters.get('state', [None])[0]

        # Imprimir los valores de los parámetros de la consulta
        print("Authorization Code:", authorization_code)
        print("State:", state)

        # Responder con un mensaje de éxito
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'PUEDES CERRAR EL NAVEGADOR')




    






def StartWebServerUserAuth(PORT):
    global authorization_code, state
    authorization_code = None
    state = None
    server = HTTPServer(('localhost', PORT), RequestHandlerUserAuth)
    print('Servidor web escuchando en el puerto', PORT)


    server.handle_request()

    # def serve():
    #     server.handle_request()
    #     return

    # # Crear un hilo para manejar las solicitudes
    # threading.Thread(target=serve).start()

    # # Esperar a que lleguen las solicitudes
    # while authorization_code is None or state is None:
    #     pass

    return authorization_code, state




    server.handle_request()