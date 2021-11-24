import socket
import sys
import time
import os
import watchdog
import random
import string

CLIENT_PORT = int(sys.argv[1])

def get_data(s):
    data = s.recv(1024)
    string = data.decode('utf-8')
    if string == "new user":
        print("nice")
    print(string)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', CLIENT_PORT))
    server.listen(5)
    while True:
        client_socket, client_address = server.accept()
        print('Connection from: ', client_address)
        get_data(client_socket)
        # data = client_socket.recv(100)
        # print('Received: ', data)
        client_socket.close()
        print('Client disconnected')