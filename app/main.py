# Uncomment this to pass the first stage
from http import HTTPStatus
import socket
from typing import List
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
    def __init__(self, request : HttpRequest, allow_routes: List[str]) -> None:
        self.request = request
        self.version = HTTP_VERSION
        self.status_code = None
        self.status_text = None
        self.body = None
        self.allow_routes = allow_routes
        self.process()
        self.get_response()

    def process(self):
        base = '/'+self.get_params()[0]
        if base not in self.allow_routes:
            self.status_code = HTTPStatus.NOT_FOUND
            self.status_text = 'Not Found'
        else:
            self.status_code = HTTPStatus.OK
            self.status_text = 'OK'

    def get_params(self):
        params = self.request.path.split('/')[1:]
        return params

    def get_response(self):
        self.response_text = f'{self.version} {self.status_code} {self.status_text}{CRLF}{CRLF}'

def main():
    server_socket = socket.create_server(
        (ADDRESS, PORT), 
        family=socket.AF_INET, # AF_INET is for IPv4 https://man7.org/linux/man-pages/man2/socket.2.html
        reuse_port=True
    )
    allow_routes = ["/", "/echo"]
    print(f"Server listening on {ADDRESS}:{PORT}")
    while True:
        client_connection, address = server_socket.accept()
        print(f"Connection from {address} has been accepted.")
        request_data = client_connection.recv(1024)
        request = HttpRequest(request_data)
        response = HttpResponse(request, allow_routes)
        # route = request_path.split('/')[1:]
        # print(f'route : {route}')
        # base = "/"+route[0]
        # if base not in allow_routes:
        #     status_line = f"{HTTP_VERSION} {HTTPStatus.NOT_FOUND} Not Found{CRLF}{CRLF}"
        # else:
        #     body = '/'.join(map(str, route[1:]))
        #     headers = {
        #         'Content-Type' : 'text/plain',
        #         'Content-Length' : len(body)
        #     }
        #     line = ''
        #     for key, value in headers.items():
        #         line += f'{key}: {value} \n'
        #     print(body)
        #     status_line = f"{HTTP_VERSION} {HTTPStatus.OK}{CRLF}{line}{CRLF}{body}{CRLF}"

        # print(repr(response).encode())

        print(response.response_text)
        client_connection.sendall(response.response_text.encode())
        client_connection.close()


if __name__ == "__main__":
    main()
