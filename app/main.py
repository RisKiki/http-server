# Uncomment this to pass the first stage
from http import HTTPStatus
import socket
ADDRESS = "localhost"
PORT = 4221
HTTP_VERSION = "HTTP/1.1"
# https://developer.mozilla.org/en-US/docs/Glossary/CRLF
CRLF = "\r\n"

def decode_http_request(request):
    """
    Decodes an HTTP request.
    """
    request_lines = request.split(CRLF)
    request_line = request_lines[0]
    request_method, request_path, request_version = request_line.split(" ")
    headers = request_lines[1:]
    headers = [header.split(": ") for header in headers]
    headers = {header[0]: header[1] for header in headers}
    print(f"Request method: {request_method}")
    print(f"Request path: {request_path}")
    print(f"Request version: {request_version}")
    print(f"Request headers: {headers}")
    return request_method, request_path, request_version, headers

def main():
    server_socket = socket.create_server(
        (ADDRESS, PORT), 
        family=socket.AF_INET, # AF_INET is for IPv4 https://man7.org/linux/man-pages/man2/socket.2.html
        reuse_port=True
    )
    allow_routes = ["/"]
    print(f"Server listening on {ADDRESS}:{PORT}")
    while True:
        client_connection, address = server_socket.accept()
        print(f"Connection from {address} has been accepted.")
        request_data = client_connection.recv(1024)
        request_method, request_path, request_version, headers = decode_http_request(request_data.decode("utf-8"))
        if request_path not in allow_routes:
            status_line = f"{HTTP_VERSION} {HTTPStatus.NOT_FOUND} Not Found{CRLF}{CRLF}"
        else:
            status_line = f"{HTTP_VERSION} {HTTPStatus.OK} OK{CRLF}{CRLF}"
        client_connection.sendall(status_line.encode())
        client_connection.close()


if __name__ == "__main__":
    main()
