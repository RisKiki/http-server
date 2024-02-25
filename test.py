class HttpResponse:
    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def generate_response_text(self):
        headers_text = '\r\n'.join([f'{key}: {value}' for key, value in self.headers.items()])
        response_text = f'HTTP/1.1 {self.status_code}\r\n{headers_text}\r\n\r\n{self.body}'
        return response_text

class Server:
    def __init__(self):
        pass

    def process_request(self, client_connection):
        # Création d'une réponse HTTP
        status_code = '200 OK'
        headers = {'Content-Type': 'text/plain'}
        body = 'Hello, world!'
        response = HttpResponse(status_code, headers, body)

        # Génération du texte de réponse
        response_text = response.generate_response_text()

        # Envoi de la réponse au client
        client_connection.sendall(response_text.encode())

def main():
    # Création d'une instance du serveur
    server = Server()

    # Simulation d'une connexion client
    fake_client_connection = FakeClientConnection()

    # Traitement de la requête
    server.process_request(fake_client_connection)

class FakeClientConnection:
    def sendall(self, data):
        # Simulation de l'envoi de données au client
        print("Envoi de la réponse au client :")
        print(data)

if __name__ == "__main__":
    main()
