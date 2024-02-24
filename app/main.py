# Uncomment this to pass the first stage
from http import HTTPStatus
import socket
from typing import Callable
ADDRESS = "localhost"
PORT = 4221
HTTP_VERSION = "HTTP/1.1"
CRLF = "\r\n"


class HttpRequest:
    def __init__(self, request_bytes: bytes):
        self.decode_http_request(request_bytes)

    def decode_http_request(self, request_bytes: bytes):
        """
        Decodes an HTTP request. 
        """
        try:
            self.request_text = request_bytes.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError("Error decoding request bytes") from e
        request_lines = self.request_text.split(CRLF)
        request_line = request_lines[0]
        request_method, request_path, request_version = request_line.split(" ")
        headers = [header for header in request_lines[1:] if header != ""]
        headers = [header.split(": ") for header in headers]
        headers = {header[0]: header[1] for header in headers}
        self.method = request_method
        self.path = request_path
        self.version = request_version
        self.headers = headers

class HttpResponse:
    def __init__(self, request : HttpRequest, routes: dict[str : Callable]) -> None:
        self.request = request
        self.version = HTTP_VERSION
        self.status_code = None
        self.status_text = None
        self.body = None
        self.headers = None
        self.routes = routes
        self.process()

    def process(self):
        base = '/'+self.get_params()[0]
        route_function = self.routes.get(base)
        if route_function:
            self.status_code = HTTPStatus.OK
            self.status_text = 'OK'
            body, headers = route_function(self.request, self.get_params()[1:])
            self.get_headers_text(headers)
            self.body = body
        else:
            self.status_code = HTTPStatus.NOT_FOUND
            self.status_text = 'Not Found'

        self.response()

    def get_headers_text(self, headers : dict):
        line = ''
        if headers:
            for key, value in headers.items():
                    line += f'{key}: {value} {CRLF}'
        self.headers = line

    def get_params(self):
        params = self.request.path.split('/')[1:]
        return params

    def response(self):
        headers = self.headers if self.headers else ''
        body = self.body if self.body else ''
        self.response_text = f'{self.version} {self.status_code} {self.status_text}{CRLF}{headers}{CRLF}{body}'


def stage_3(request, params):
    return None, None

def stage_4(request, params):
    body = '/'.join(map(str, params))
    headers = {
        'Content-Type' : 'text/plain',
        'Content-Length' : len(body)
    }
    return body, headers

def stage_5(request:HttpRequest, params):
    body = request.headers.get('User-Agent')
    headers = {
        'Content-Type' : 'text/plain'
    }
    return body, headers

def main():
    server_socket = socket.create_server(
        (ADDRESS, PORT), 
        family=socket.AF_INET, # AF_INET is for IPv4 https://man7.org/linux/man-pages/man2/socket.2.html
        reuse_port=True
    )
    routes = {
        "/" : stage_3,
        "/echo" : stage_4,
        "/user-agent" : stage_5,

    }
    print(f"Server listening on {ADDRESS}:{PORT}")
    while True:
        client_connection, address = server_socket.accept()
        print(f"Connection from {address} has been accepted.")
        request_data = client_connection.recv(1024)
        request = HttpRequest(request_data)
        response = HttpResponse(request, routes)
        print(response.response_text)
        client_connection.sendall(response.response_text.encode())
        client_connection.close()


if __name__ == "__main__":
    main()
