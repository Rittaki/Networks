# Networks
In order to run files:
open the server from one computer, from the other one open the client
server.py - gets as arguments port number
client.py - get as arguments: 1) IP of the server 2) port number of the server 3) path to the directory to monitor 4) fixed time (in seconds) to connect with the server. Optional 5) id of the user. If no last argument provided, the server creates new id for the current client and sends it to the him so the next time this client connects from the other device, he can syncronize all the existing files.
