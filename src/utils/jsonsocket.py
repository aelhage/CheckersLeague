# file:jsonsocket.py
# https://github.com/mdebbar/jsonsocket
import json
import socket


class Server(object):
    """
    A JSON socket server used to communicate with a JSON socket client. All the
    data is serialized in JSON. How to use it:

    server = Server(host, port)
    while True:
    server.accept()
    data = server.recv()
    # shortcut: data = server.accept().recv()
    server.send({'status': 'ok'})
    """

    def __init__(self, host, port, timeout):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(timeout)
        self.socket.bind((host, port))
        self.socket.listen(5)
        self.client_addr = None

    def __del__(self):
        self.close()

    def accept(self):
        return self.socket.accept()

    def send(self, client, data):
        if not client:
            raise Exception('Cannot send data, no client is connected')
        json_send(client, data)
        return self

    def recv(self, client):
        if not client:
            raise Exception('Cannot receive data, no client is connected')
        return json_recv(client)

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None


class Client(object):
    """
    A JSON socket client used to communicate with a JSON socket server. All the
    data is serialized in JSON. How to use it:

    data = {
    'name': 'Patrick Jane',
    'age': 45,
    'children': ['Susie', 'Mike', 'Philip']
    }
    client = Client()
    client.connect(host, port)
    client.send(data)
    response = client.recv()
    # or in one line:
    response = Client().connect(host, port).send(data).recv()
    """

    socket = None

    def __del__(self):
        self.close()

    def connect(self, host, port, timeout):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        self.socket.settimeout(timeout)
        return self

    def setblocking(self, flag):
        self.socket.setblocking(flag)

    def settimeout(self, timeout):
        self.socket.settimeout(timeout)

    def send(self, data):
        if not self.socket:
            raise Exception('You have to connect first before sending data')
        json_send(self.socket, data)
        return self

    def recv(self):
        if not self.socket:
            raise Exception('You have to connect first before receiving data')
        return json_recv(self.socket)

    def recv_and_close(self):
        data = self.recv()
        self.close()
        return data

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None


# helper functions #
def json_send(socket, data):
    print(data)
    try:
        serialized = json.dumps(data)
    except (TypeError, ValueError):
        raise Exception('You can only send JSON-serializable data')
    # send the length of the serialized data first
    socket.send(('%d\n' % len(serialized)).encode())
    # send the serialized data
    socket.sendall(serialized.encode())


def json_recv(socket):
    # read the length of the data, letter by letter until we reach EOL
    length_str = ''
    char = str(socket.recv(1).decode())
    while char != '\n':
        length_str += char
        char = str(socket.recv(1).decode())
    total = int(length_str)
    # use a memoryview to receive the data chunk by chunk efficiently
    view = memoryview(bytearray(total))
    next_offset = 0
    while total - next_offset > 0:
        recv_size = socket.recv_into(view[next_offset:], total - next_offset)
        next_offset += recv_size
    try:
        deserialized = json.loads(view.tobytes())
    except (TypeError, ValueError):
        raise Exception('Data received was not in JSON format')
    return deserialized