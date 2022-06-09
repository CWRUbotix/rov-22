# echo-client.py

import socket

HOST = "192.168.2.2"  # The server's hostname or IP address
PORT = 60000  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes([3, 0]))
