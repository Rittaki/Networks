import socket
import sys
import time
import os
import watchdog
import random
import string

CLIENT_PORT = int(sys.argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 12345))
server.listen(5)

while True:
    client_socket, client_address = server.accept()
    print('Connection from: ', client_address)

    data = client_socket.recv(100)
    print('Received: ', data)

    client_socket.send(data.upper())

    client_socket.close()
    print('Client disconnected')