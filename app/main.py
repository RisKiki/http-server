# Uncomment this to pass the first stage
import argparse
from http import HTTPStatus
import os
import socket
import multiprocessing
from typing import Callable

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

    def get_status_text_from_code(self, code : HTTPStatus):
        if code == HTTPStatus.OK:
            return 'OK'
        elif code == HTTPStatus.NOT_FOUND:
            return 'Not Found'
        else:
            return 'Error'

    def process(self):
        base = '/'+self.get_params()[0]
        route_function = self.routes.get(base)
        if route_function:
            self.status_code = HTTPStatus.OK
            res = route_function(self.request, self.get_params()[1:])
            if len(res) == 2:
                body, headers = res
            if len(res) == 3:
                body, headers, status_code = res
                self.status_code = status_code
            else:
                headers = {}
                body = ''
            self.body = body
            self.get_headers_text(headers)
        else:
            self.status_code = HTTPStatus.NOT_FOUND
        
        self.status_text = self.get_status_text_from_code(self.status_code)
        self.response()

    def get_headers_text(self, headers : dict):
        line = ''
        if headers:
            if self.body:
                headers = {**headers, 'Content-Length' : len(self.body)}
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

class Server:
    def __init__(self, ip, port, routes):
        self.port = port
        self.ip = ip
        self.routes = routes

    def start(self):
        self.server_socket = socket.create_server(
            (self.ip, self.port), 
            family=socket.AF_INET, # AF_INET is for IPv4 https://man7.org/linux/man-pages/man2/socket.2.html 
            reuse_port=True
        )
        print(f"Server listening on {self.ip}:{self.port}")
        while True:
            client_connection, address = self.server_socket.accept()
            multiprocessing.Process(target=self.process, args=(client_connection, address)).start()

    def process(self, client_connection, address):
        print(f"Connection from {address} has been accepted.")
        request_data = client_connection.recv(1024)
        request = HttpRequest(request_data)
        response = HttpResponse(request, self.routes)
        print("zizi")
        print(response.response_text)
        client_connection.sendall(response.response_text.encode())
        client_connection.close()
        
def stage_3(request, params):
    return None, None

def stage_4(request, params):
    body = '/'.join(map(str, params))
    headers = {
        'Content-Type' : 'text/plain'
    }
    return body, headers

def stage_5(request:HttpRequest, params):
    body = request.headers.get('User-Agent')
    headers = {
        'Content-Type' : 'text/plain'
    }
    return body, headers

def stage_7(requst:HttpRequest, params):
    headers = {
        'Content-Type':'application/octet-stream'
    }
    filename = params[0]
    path = filename+directory
    check_file = os.path.isfile(path)
    if check_file:
        f = open(path, "r")
        body = f.read()
        return body, headers
    else:
        status_code = HTTPStatus.NOT_FOUND
        return None, headers, status_code


def parse_args():
    parser = argparse.ArgumentParser(description='Run the Flask application with specified environment.')
    parser.add_argument('--directory', default='dev', help='Specify the environment (default: dev)')
    return parser.parse_args()


def main():
    args = parse_args()
    global directory
    directory = args.directory
    routes = {
        "/" : stage_3,
        "/echo" : stage_4,
        "/user-agent" : stage_5
    }
    server = Server("localhost", 4221, routes)
    server.start()


if __name__ == "__main__":
    main()
