# Python TCP Client A
import socket
import time
from utils.jsonsocket import Client
from msgs.messages import *

host = socket.gethostname() 
port = 2004
BUFFER_SIZE = 2000
dataobj = ConnectionRequest('hello world')
data = dict(dataobj)

client = Client()
client.connect(host, port)
client.send(data)

while True:
    response = client.recv()
    print('here')

    try:
        w4o = WaitingForOpponent()
        w4o.from_dict(response)

        if w4o.flag is None:
            raise Exception("invalid")

        print(w4o.flag)

    except Exception:
        print("Invalid Message.")
        continue

client.close()
