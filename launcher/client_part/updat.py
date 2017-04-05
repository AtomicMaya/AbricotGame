import sqlite3
import os
import os.path
import hashlib
import time
import requests
from ftg import *
import socket

file = "RELEASE.manifest"
exist = os.path.isfile("RELEASE")
if exist:
    f = open(file,"r")
    version = f.read()
else:
    version = 0

server_version = 0
temp = requests.get("http://devssda.orgfree.com/version.html")
server_version = temp.text
update_server_ip = requests.get("http://devssda.orgfree.com/update_ip.html")

ftp = Ftp_client(update_server_ip, 21, "client", "123", 5)

if version < server_version:
    ftp.download_file(os.getcwd(), '', 'RELEASE.manifest')
    f = open(file,"r")
    version = f.read()
elif version > server_version:
    version = 0

if version != server_version:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((update_server_ip, 40442)) # Error 404, received 42
    sock.send(str(version).encode())
    table_distant_name = sock.recv(1024).decode()
    ftp.download_file(os.getcwd(), 'temp', table_distant_name)

    
    
    
print(server_version)
    
