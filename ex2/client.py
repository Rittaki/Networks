import socket
import sys
import time
import os
import random
import string
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
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
        self.client.close()

class EventHandler(FileSystemEventHandler):
    def __init__(self, path, client):
        # self.observer = Observer()
        self.path = path
        self.client = client

    # on_any_event function - delete later
    def on_any_event(self, event):
        if event.is_directory:
            print("is directory")
        if event.event_type == 'created':
            print("created")
        if event.event_type == 'modified':
            print("modified")
        if event.event_type == 'moved':
            print("moved")
        if event.event_type == 'deleted':
            print("deleted")

    def on_created(self, event):
        pass

    def on_modified(self, event):
        pass

    def on_moved(self, event):
        pass

    def on_deleted(self, event):
        pass

def send_new_user_files(directory, client):
    for path, folders, files in os.walk(directory):
        for file in files:
            pass
            print("path_to_send: " + path)
            print("file name: " + file)
            client.send("file,".encode('utf-8') + os.path.join(path, file).encode('utf-8'))
            client.recv(1024)
            # change "end of file" to while(data) in server.py
            client.send("end of file".encode('utf-8'))
            client.recv(1024)
        for folder in folders:
            # pass
            print("folder: " + folder)
            client.send("folder,".encode('utf-8') + os.path.join(path, folder).encode('utf-8'))
            client.recv(1024)
    client.send("finish".encode('utf-8'))

def create_file(id_num, file, path, user_folder):
    try:
        relative_path = path.split(os.sep, 1)[1]
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

def create_folder(folder, path, user_folder):
    try:
        relative_path = path.split(os.sep, 1)[1]
    except:
        relative_path = ""
    new_dir = os.path.join(user_folder, relative_path, folder)
    os.makedirs(new_dir, exist_ok=True)

def pull_files(id_num, client):
    # id_folder = os.path.join(os.getcwd(), id_num)
    user_folder = os.path.join(os.getcwd(), DIR_PATH)
    os.makedirs(user_folder, exist_ok=True)
    for path, folders, files in os.walk(id_num):
        for file in files:
            create_file(id_num, file, path, user_folder)
        for folder in folders:
            create_folder(folder, path, user_folder)

if __name__ == '__main__':
    # creating new socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CLIENT_IP, PORT))
    try:
        IDENTIFY = sys.argv[5]
        s.send("old user,".encode('utf-8') + IDENTIFY.encode('utf-8'))
        pull_files(IDENTIFY, s)
    except:
        s.send("new user,".encode('utf-8') + DIR_PATH.encode('utf-8'))
        IDENTIFY = s.recv(129).decode('utf-8')
        print("id is: " + str(IDENTIFY))
        send_new_user_files(DIR_PATH, s)

    watch = Watcher(DIR_PATH, s)
    watch.run()

