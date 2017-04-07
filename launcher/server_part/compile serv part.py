import sqlite3
import os
import os.path
import hashlib
import time
import requests
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 40442))
sock.listen(5)
connected = []

on = True
while on:
    current, wl, xl = select.select([sock], [], [], 0.05)
        for _ in current:
            temp, message = _.accept()
            client_version = int(temp.recv(1024).decode())
