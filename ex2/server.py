import socket
import sys
import time
import os
import watchdog
import random
import string

CLIENT_PORT = int(sys.argv[1])
clients = {}

# create new user's folder with id number name
def create_new_user_folder(identifier, comp_id):
    os.mkdir(os.path.join(os.getcwd(), identifier))
    clients[(identifier, comp_id)] = []

def create_id():
    return ''.join(random.choices(string.ascii_lowercase + string.ascii_uppercase + string.digits, k=128))

def create_comp_id():
    return ''.join(random.choices(string.digits, k=20))

def client_exists(client):
    if os.path.exists(os.path.join(os.getcwd(), client)):
        return True
    return False

# create new file on server
def create_file(id_num, path):
    file_path = os.path.join(os.getcwd(), path)
    open_file = open(file_path, 'rb')
    content = open_file.read(1024)
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), id_num, relative_path)
    file = open(current_path, 'wb')
    while content:
        file.write(content)
        content = open_file.read(1024)
    file.close()

# create new folder on server
def create_folder(id_num, path):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), id_num, relative_path)
    os.makedirs(current_path, exist_ok=True)

# create all the items of new user
def create_items(id_num, path):
    for root, folders, files in os.walk(path):
        for file in files:
            create_file(id_num, os.path.join(root, file))
        for folder in folders:
            create_folder(id_num, os.path.join(root, folder))

# delete file/folder on server
def delete_item(id_num, path):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), id_num, relative_path)
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

# change name of file/folder
def change_name(id_num, src, dest):
    try:
        relative_src = src.split(os.path.sep, 1)[1]
    except:
        relative_src = ""
    src_path = os.path.join(os.getcwd(), id_num, relative_src)
    try:
        relative_dest = dest.split(os.path.sep, 1)[1]
    except:
        relative_dest = ""
    dest_path = os.path.join(os.getcwd(), id_num, relative_dest)
    os.rename(src_path, dest_path)

def get_updates(identifier, comp_id, command):
    # path = os.path.join(os.getcwd(), identifier)
    # print("Client's path is: " + path)
    if command == 'NEW_FOLDER':
        print("Got new folder")
        path = client_file.readline().strip().decode()
        create_folder(identifier, path)
        create_items(identifier, path)
    elif command == 'NEW_FILE':
        print("Got new file")
        path = client_file.readline().strip().decode()
        create_file(identifier, path)
    elif command == 'DELETE':
        print("Deleting file/folder...")
        path = client_file.readline().strip().decode()
        delete_item(identifier, path)
    elif command == 'MOD_FILE':
        print("Changing file...")
        path = client_file.readline().strip().decode()
        delete_item(identifier, path)
        create_file(identifier, path)
    elif command == 'MOVED':
        print("Changing name...")
        src = client_file.readline().strip().decode()
        dest = client_file.readline().strip().decode()
        change_name(identifier, src, dest)

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', CLIENT_PORT))
    server.listen()
    while True:
        client_socket, client_address = server.accept()
        with client_socket, client_socket.makefile("rb") as client_file:
            print('Connection from: ', client_address)
            identifier = client_file.readline().strip().decode()
            print("ID is: " + identifier)
            computer_id = client_file.readline().strip().decode()
            print("Computer ID is: " + computer_id)
            if client_exists(identifier):
                command = client_file.readline().strip().decode()
                if command == 'NEW_COMP':
                    computer_id = create_comp_id()
                    clients[(identifier, computer_id)] = []
                    client_socket.sendall(computer_id.encode() + b'\n')
                else:
                    get_updates(identifier, computer_id, command)
            else:
                print("Not existing client")
                computer_id = create_comp_id()
                print("Created computer ID is: " + computer_id)
                identifier = create_id()
                create_new_user_folder(identifier, computer_id)
                client_socket.sendall(identifier.encode() + b'\n')
                client_socket.sendall(computer_id.encode() + b'\n')
                user_dir = client_file.readline().strip().decode()
                print("User dir is: " + user_dir)
                create_items(identifier, user_dir)
            client_socket.close()
