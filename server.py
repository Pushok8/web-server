import socket as sock
import time
import mimetypes

PATH = {
    '/': 'index.html',
    '/blog': './blog/index.html'
}


class HttpResponse:
    """
    This class implementation standard http response from server to client.
    HttpResponse accept:
        code: int -> http code;
        msg: str -> if have, http message;
        content-type:str -> mime-type content
        content: bytes -> content that is transmitted to the client.
    """
    current_date = time.strftime('%a, %d %b %Y %H:%M:%S %Z')
    http_response_template = (
        'HTTP/1.1 {code} {msg}\r\n'
        'Date: {current_date}\r\n'
        'Server: localhost\r\n'
        'Content-Length: {content_length}\r\n'
        'Content-Type: {content_type}\r\n\r\n'
    )

    def __init__(self, code: int, content_type: str, content: bytes, msg: str = '') -> None:
        self.code: int = code
        self.msg: str = msg
        self.content_type = content_type
        self.content = content
        self.content_length = len(content)

    def get_http_response(self):
        """
        Create http response by template:
            HTTP/1.1 {code} {msg}
            Date: {current_date}
            Server: localhost
            Content-Length: {content_length}
            Content-Type: {content_type}

            {content}
        """
        return self.http_response_template.format(
            code=self.code,
            msg=self.msg,
            current_date=self.current_date,
            content_length=self.content_length,
            content_type=self.content_type
        ).encode('utf-8') + self.content

    def __str__(self):
        return self.http_response_template.format(
            code=self.code,
            msg=self.msg,
            current_date=self.current_date,
            content_length=self.content_length,
            content_type=self.content_type
        ) + self.content.decode('UTF-8')


def get_content_by_request(client_request: str):
    """
        Looking for required path and return http response with 200 code and content from required path.
     If it path not found, returns 404 code and content with message: 'This page not found'. If raised an error on
     server side, returns 500 code and content with message: 'No file was found on the server at the specified path'.
     If method in client request is not GET, returns 403 code and content with message: 'Method not allowed'.

    :param client_request: http request from client.
    :return: http response from server.
    """
    parsed_request = client_request.split(b' ')
    have_path = PATH.get(parsed_request[1].decode('UTF-8'), False)

    if have_path:
        try:
            with open(have_path, 'rb') as file:
                content_type = mimetypes.guess_type(have_path)[0]
                content = file.read()
                return HttpResponse(200, content_type, content, 'OK').get_http_response()
        except FileNotFoundError:
            return HttpResponse(500, 'text/html', b'<h1>500</h1><p>No file was found on the server'
                                                  b' at the specified path.</p>').get_http_response()

    elif not have_path:
        return HttpResponse(404, 'text/html', b'<h1>404</h1><p>This page not found</p>',
                            'Not found').get_http_response()

    elif parsed_request[0].decode('UTF-8').upper() != 'GET':
        return HttpResponse(403, 'text/html', b'<h1>403</h1><p>Method not allowed</p>',
                            'Method not allowed').get_http_response()


def run_server():
    server = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
    server.bind(('localhost', 2020))
    server.listen()

    while True:
        client, client_address = server.accept()
        request = client.recv(4098)
        print(f'On server connected client by:\n'
              f'IP: {client_address[0]}\n'
              f'Port: {client_address[1]}\n'
              f'He send on server:\n\n{request.decode("utf-8")}', end='')
        print('_' * 150)
        client.sendall(get_content_by_request(request))
        client.close()


if __name__ == '__main__':
    run_server()
