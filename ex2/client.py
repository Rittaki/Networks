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
        try:
            path_to_send = path.split("/", 1)[1]
        except:
            path_to_send = ""
        for file in files:
            # pass
            print("path_to_send: " + path_to_send)
            print("file name: " + file)
            # s.send("file,".encode('utf-8') + (path_to_send + "/" + file).encode('utf-8'))
            s.send("file,".encode('utf-8') + os.path.join(path_to_send, file).encode('utf-8'))
            s.recv(1024)
            # change "end of file" to while(data) in server.py
            s.send("end of file".encode('utf-8'))
            s.recv(1024)
        for folder in folders:
            print("folder: " + folder)
            # s.send("folder,".encode('utf-8') + (path + "/" + folder).encode('utf-8'))
            s.send("folder,".encode('utf-8') + os.path.join(path_to_send, folder).encode('utf-8'))
            s.recv(1024)

    s.send("finish".encode('utf-8'))

if __name__ == '__main__':
    # creating new socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((CLIENT_IP, PORT))
    try:
        IDENTIFY = sys.argv[5]
    except:
        s.send("new user,".encode('utf-8') + DIR_PATH.encode('utf-8'))
        IDENTIFY = s.recv(129).decode('utf-8')
        print("id is: " + str(IDENTIFY))
        send_new_user_files(DIR_PATH, s)

    watch = Watcher(DIR_PATH, s)
    watch.run()

