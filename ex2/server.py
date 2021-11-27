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
    # print("FILE PATH IS: ", file_path)
    open_file = open(file_path, 'rb')
    content = open_file.read(1024)
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), id_num, relative_path)
    # current_path = os.path.join(clients.get(id_num), relative_path)
    # print("current_path is: " + current_path)
    file = open(current_path, 'wb')
    while content:
        file.write(content)
        content = open_file.read(1024)
    file.close()

# TO DO: create_item - recursive creation - send from client to server just a path of
# user's folder and server is making recursive creation of folders and files (like in deleting)
# (maybe split to calling for two functions: create_folder and create_file)
def create_folder(id_num, path):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), id_num, relative_path)
    # current_path = os.path.join(clients.get(id_num), relative_path)
    # print("current_path is: ", current_path)
    os.makedirs(current_path, exist_ok=True)

def get_files_new(client, id_num):
    # to do: while(data):
    data = client.recv(1024).decode('utf-8')
    # print("data is: " + data)
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
            # print("path is: ", path)
            create_file(id_num, path)
            data = client.recv(1024).decode('utf-8')
            # print(data)
            while data != "end of file":
                data = client.recv(1024).decode('utf-8')
                # print(data)
            client.send("next".encode('utf-8'))
        data = client.recv(1024).decode('utf-8')
        # print(data)

def delete_item(id_num, path):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), id_num, relative_path)
    # current_path = os.path.join(clients.get(id_num), relative_path)
    if os.path.exists(current_path):
        if os.path.isdir(current_path):
            for root, folders, files in os.walk(current_path, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for folder in folders:
                    os.rmdir(os.path.join(root, folder))
            os.rmdir(current_path)
        else:
            os.remove(current_path)

def get_data(s):
    while True:
        data = s.recv(1024)
        print(data)
        data = data.decode('utf-8')
        string = data.split(",")[0]
        if string == "new user":
            id_num = create_id()
            # print(id_num)
            s.send(str.encode(id_num))
            create_new_user_folder(id_num)
            get_files_new(s, id_num)
        if string == "NEW_FOLDER":
            print("got new folder")
            path = data.split(",")[1]
            create_folder(path.split(os.path.sep, 1)[0], path.split(os.path.sep, 1)[1])
        if string == "NEW_FILE":
            print("got new file")
            path = data.split(",")[1]
            create_file(path.split(os.path.sep, 1)[0], path.split(os.path.sep, 1)[1])
        if string == "DELETE":
            print("deleting file/folder...")
            path = data.split(",")[1]
            delete_item(path.split(os.path.sep, 1)[0], path.split(os.path.sep, 1)[1])
        if string == "MODIFIED":
            print("changing file...")
            path = data.split(",")[1]
            delete_item(path.split(os.path.sep, 1)[0], path.split(os.path.sep, 1)[1])
            create_file(path.split(os.path.sep, 1)[0], path.split(os.path.sep, 1)[1])

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