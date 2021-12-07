import socket
import sys
import time
import os
import random
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

CLIENT_IP = sys.argv[1]
PORT = int(sys.argv[2])
DIR_PATH = sys.argv[3]
PERIOD = sys.argv[4]

class Watcher:
    def __init__(self, path, client):
        self.observer = Observer()
        self.path = path
        self.client = client

    def run(self):
        event_handler = EventHandler(self.path, self.client)
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                if self.client.timer + int(PERIOD) < time.time():
                    self.client.setup_connection()
                    self.client.new_update()
                    self.client.close_connection()
                time.sleep(int(PERIOD))
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class EventHandler(FileSystemEventHandler):
    def __init__(self, path, client):
        self.path = path
        self.client = client

    def on_any_event(self, event):
        time.sleep(0.5)
        if any(str(event.src_path).startswith(s) for s in self.client.ignore_watch):
            if event.src_path in self.client.ignore_watch:
                self.client.ignore_watch.remove(event.src_path)
            return

        self.client.setup_connection()

        if event.event_type == 'created':
            print(f"{event.src_path} created")
            if os.path.isdir(event.src_path):
                self.client.socket.sendall('NEW_FOLDER'.encode() + b'\n')
                self.client.socket.sendall(event.src_path.encode() + b'\n')
            else:
                self.client.socket.sendall('NEW_FILE'.encode() + b'\n')
                self.client.socket.sendall(event.src_path.encode() + b'\n')
        elif event.event_type == 'deleted':
            print(f"{event.src_path} deleted")
            self.client.socket.sendall('DELETE'.encode() + b'\n')
            self.client.socket.sendall(event.src_path.encode() + b'\n')
        elif event.event_type == 'moved':
            print(f"{event.src_path} moved")
            self.client.socket.sendall('MOVED'.encode() + b'\n')
            self.client.socket.sendall(event.src_path.encode() + b'\n')
            self.client.socket.sendall(event.dest_path.encode() + b'\n')
        elif event.event_type == 'modified':
            print(f"{event.src_path} modified")
            if os.path.isdir(event.src_path):
                pass
                # self.client.socket.sendall('MOD_FOLDER'.encode() + b'\n')
                # self.client.socket.sendall(event.src_path.encode() + b'\n')
            else:
                self.client.socket.sendall('MOD_FILE'.encode() + b'\n')
                self.client.socket.sendall(event.src_path.encode() + b'\n')
        self.client.close_connection()

def change_name(user_folder, src, dest):
    try:
        relative_src = src.split(os.path.sep, 1)[1]
    except:
        relative_src = ""
    src_path = os.path.join(os.getcwd(), user_folder, relative_src)
    try:
        relative_dest = dest.split(os.path.sep, 1)[1]
    except:
        relative_dest = ""
    dest_path = os.path.join(os.getcwd(), user_folder, relative_dest)
    os.rename(src_path, dest_path)

def delete_item(path, user_folder):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    current_path = os.path.join(os.getcwd(), user_folder, relative_path)
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

# creates file on user's computer
def create_file(id_num, file, path, user_folder):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""

    file_path = os.path.join(os.getcwd(), id_num, relative_path)
    open_file = open(os.path.join(file_path, file), 'rb')
    content = open_file.read(1024)

    current_path = os.path.join(user_folder, relative_path, file)
    f = open(current_path, 'wb')
    while content:
        f.write(content)
        content = open_file.read(1024)
    f.close()

# creates folder on user's computer
def create_folder(folder, path, user_folder):
    try:
        relative_path = path.split(os.path.sep, 1)[1]
    except:
        relative_path = ""
    new_dir = os.path.join(user_folder, relative_path, folder)
    os.makedirs(new_dir, exist_ok=True)

# pull all the files from server when old client connects from new computer
def pull_files(id_num):
    user_folder = os.path.join(os.getcwd(), DIR_PATH)
    os.makedirs(user_folder, exist_ok=True)
    for path, folders, files in os.walk(id_num):
        for file in files:
            create_file(id_num, file, path, user_folder)
        for folder in folders:
            create_folder(folder, path, user_folder)

class Client:
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.file = self.socket.makefile('rb')
        self.id_num = '0'
        self.computer = '0'
        self.timer = time.time()
        self.ignore_watch = list()

    def run(self):
        try:
            self.id_num = str(sys.argv[5])
            self.setup_connection()
            self.socket.sendall('NEW_COMP'.encode() + b'\n')
            self.computer = self.file.readline().strip().decode()
            pull_files(self.id_num)
        except:
            self.setup_connection()
            self.id_num = self.file.readline().strip().decode()
            print("ID is: " + self.id_num)
            self.computer = self.file.readline().strip().decode()
            print("Computer ID is: " + self.computer)
            self.socket.sendall(DIR_PATH.encode() + b'\n')
        self.close_connection()
        self.timer = time.time()

    def setup_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((CLIENT_IP, PORT))
        self.file = self.socket.makefile("rb")
        self.socket.sendall(self.id_num.encode() + b'\n')
        self.socket.sendall(self.computer.encode() + b'\n')

    def close_connection(self):
        self.socket.close()
        self.file.close()

    def new_update(self):
        self.socket.sendall('SYNC'.encode() + b'\n')
        number = self.file.readline().strip().decode()
        for update in range(int(number)):
            command = self.file.readline().strip().decode()
            if command == 'NEW_FILE':
                paths = self.file.readline().strip().decode()
                file_name = paths.split(os.path.sep)[-1]
                path_no_file = os.path.split(paths)[0]
                # path_no_file = os.path.dirname(os.path.abspath(file_name))
                create_file(self.id_num, file_name, path_no_file, DIR_PATH)
                path_no_dir = paths.split(os.path.sep, 1)[1]
                self.ignore_watch.append(os.path.join(DIR_PATH, path_no_dir))
            elif command == 'NEW_FOLDER':
                path = self.file.readline().strip().decode()
                folder_name = ''
                # folder_name = path.split(os.path.sep)[-1]
                # path_no_folder = os.path.dirname(folder_name)
                create_folder(folder_name, path, DIR_PATH)
                path_no_dir = path.split(os.path.sep, 1)[1]
                self.ignore_watch.extend([os.path.join(DIR_PATH, path_no_dir)] * 2)
            elif command == 'DELETE':
                path = self.file.readline().strip().decode()
                # item_name = path.split(os.path.sep)[-1]
                delete_item(path, DIR_PATH)
                path_no_dir = path.split(os.path.sep, 1)[1]
                self.ignore_watch.extend([os.path.join(DIR_PATH, path_no_dir)] * 3)
            elif command == 'MOVED':
                path = self.file.readline().strip().decode()
                src = path.split(',')[0]
                # src_item = src.split(os.path.sep)[-1]
                src_path_no_dir = src.split(os.path.sep, 1)[1]
                dest = path.split(',')[1]
                # dest_item = dest.split(os.path.sep)[-1]
                dest_path_no_dir = dest.split(os.path.sep, 1)[1]
                change_name(DIR_PATH, src, dest)
                self.ignore_watch.append(os.path.join(DIR_PATH, src_path_no_dir))
                self.ignore_watch.append(os.path.join(DIR_PATH, dest_path_no_dir))
        self.timer = time.time()

if __name__ == "__main__":
    c = Client()
    c.run()
    watch = Watcher(DIR_PATH, c)
    watch.run()