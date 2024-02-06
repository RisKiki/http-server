# Uncomment this to pass the first stage
from http import HTTPStatus
import socket


def main():
    ADDRESS = "localhost"
    PORT = 4221
    HTTP_VERSION = "HTTP/1.1"
    # https://developer.mozilla.org/en-US/docs/Glossary/CRLF
    CRLF = "\r\n"
    server_socket = socket.create_server(
        (ADDRESS, PORT), 
        family=socket.AF_INET, # AF_INET is for IPv4 https://man7.org/linux/man-pages/man2/socket.2.html
        reuse_port=True
    )
    while True:
        client_connection, address = server_socket.accept()
        print(f"Connection from {address} has been accepted.")
        request_data = client_connection.recv(1024)
        print(request_data.decode("utf-8"))
        status_line = f"{HTTP_VERSION} {HTTPStatus.OK} OK{CRLF}{CRLF}"
        client_connection.sendall(status_line.encode())
        client_connection.close()


if __name__ == "__main__":
    main()
