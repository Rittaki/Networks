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

if __name__ == "__main__":
    c = Client()
    c.run()
    watch = Watcher(DIR_PATH, c)
    watch.run()