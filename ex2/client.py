import socket
import sys
import time
import os
import random
import string
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SERVER_IP = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
DIR_PATH = sys.argv[3]
PERIOD = sys.argv[4]
try:
    IDENTIFY = sys.argv[5]
    if len(IDENTIFY) < 128:
        exit()
except:
    IDENTIFY = None

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER_IP, SERVER_PORT))

class Watcher:
    def __init__(self, path, socket):
        self.observer = Observer()

    def run(self):
        event_handler = EventHandler()

class EventHandler(FileSystemEventHandler):
    def __init__(self, path, socket):
        self.observer = Observer()

if __name__ == '__main__':
    watch = Watcher(DIR_PATH, s)
    watch.run()

# s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# s.connect((SERVER_IP, SERVER_PORT))
# s.send(b'hello')
#
# data = s.recv(100)
# print("Server sent: ", data)
#
# s.close()