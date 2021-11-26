import socket
import sys
import time
import os
import watchdog
import random
import string

CLIENT_PORT = int(sys.argv[1])
clients = {}


def create_new_user_folder(id_num):
    os.mkdir(id_num)
    current_dir = os.getcwd()
    clients[id_num] = os.path.join(current_dir, id_num)

def create_id():
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=128))

def create_file(id_num, path):
    file_path = os.path.join(os.getcwd(), path)
    print("FILE PATH IS: ", file_path)
    open_file = open(file_path, 'rb')
    content = open_file.read(1024)
    try:
        relative_path = path.split("/", 1)[1]
    except:
        relative_path = ""

    current_path = os.path.join(clients.get(id_num), relative_path)
    print("current_path is: " + current_path)
    file = open(current_path, 'wb')
    while content:
        file.write(content)
        content = open_file.read(1024)
    file.close()

def create_folder(id_num, path):
    try:
        relative_path = path.split("/", 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(clients.get(id_num), relative_path)
    print("current_path is: ", current_path)
    os.makedirs(current_path, exist_ok=True)

def get_files_new(client, id_num):
    # to do: while(data):
    data = client.recv(1024).decode('utf-8')
    print("data is: " + data)
    while data != "finish":
        string = data.split(",", 1)[0]
        if string == "folder":
            # pass
            path = data.split(",", 1)[1]
            client.send("next".encode('utf-8'))
            create_folder(id_num, path)
        if string == "file":
            # pass
            path = data.split(",", 1)[1]
            client.send("next".encode('utf-8'))
            print("path is: ", path)
            create_file(id_num, path)
            data = client.recv(1024).decode('utf-8')
            print(data)
            while data != "end of file":
                data = client.recv(1024).decode('utf-8')
                print(data)
            client.send("next".encode('utf-8'))
        data = client.recv(1024).decode('utf-8')
        print(data)

def get_data(s):
    data = s.recv(1024)
    data = data.decode('utf-8')
    string = data.split(",")[0]
    if string == "new user":
        path = data.split(",")[1]
        id_num = create_id()
        print(id_num)
        s.send(str.encode(id_num))
        create_new_user_folder(id_num)
        get_files_new(s, id_num)
        s.close()
    if string == "old user":
        id_num = data.split(",", 1)[1]
        print("old user is: " + str(id_num))

    print(string)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', CLIENT_PORT))
    server.listen()
    while True:
        client_socket, client_address = server.accept()
        print('Connection from: ', client_address)
        get_data(client_socket)
        # data = client_socket.recv(100)
        # print('Received: ', data)
        client_socket.close()
        print('Client disconnected')