import sqlite3
import os
import os.path
import hashlib
import time
import requests
from ftp import *
import socket
import asyncio
from threading import Thread, Timer

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Determine la version actuelle
file = "RELEASE.manifest"
exist = os.path.isfile("RELEASE.manifest")
if exist:
    f = open(file,"r")
    version = f.read()
else:
    version = 0

#Données statiques
server_version = 0
site = "http://devssda.orgfree.com"
temp = requests.get(site + "/versions.html")
server_version = temp.json()[0]
update_server_ip = "abricot.zapto.org"
print(update_server_ip)
# Créé le client ftp
ftp = Ftp_client(update_server_ip, 21, "user", "123", 1)

# Compare a la version serveur
if version != server_version:
    ftp.download_file(os.getcwd(), '', "table.sq3", "temp")

    # Gestion de la table
    conection = sqlite3.connect("temp/table.sq3")
    cursor = conection.cursor()
    cursor.execute("SELECT * FROM files")
    data = list(cursor)

# Taille totale
total = [sum([i[3] for i in data])]
# Taille déjà téléchargée
current = [0]
possible_cur = 0

def speed(current, total, interval):
    temp = current[0]
    l = []
    while current != total:
        last_sec = round((current[0]-temp)/1024, 2)
        l.append(last_sec)
        moyenne = sum(l[-20:])/20
        print("\r",round(moyenne, 2),"ko/s (ETA: %d seconds)"%int((total[0]-current[0])/(moyenne*1024+1)),"   DEBUG:current %d"%current[0],end="")
        temp = current[0]
        time.sleep(interval)
thread = Thread(None, speed, args=[current,total,1])
thread.daemon = True
thread.start()

# Parcours de la table
for file_info in data:
    # Récupération des infos
    name, path, Hash, size = file_info
    temp_path = os.path.join(os.getcwd(), "data", path[1:])
    
    # Télécharge si le fichier n'existe pas ou si le hash est différent
    exists = os.path.exists(temp_path)
    if not exists:
        try:
            os.makedirs(temp_path)
        except OSError as exc: # Guard against race condition
            print("error :",exc)
        ftp.download_file(os.getcwd(), 'data'+path, name, monitoring_var=current)
    elif os.path.isfile(os.path.join(temp_path, name)):
        if md5(os.path.join(temp_path, name)) != Hash:
            ftp.download_file(os.getcwd(), 'data'+path, name, monitoring_var=current)
    else:
        ftp.download_file(os.getcwd(), 'data'+path, name, monitoring_var=current)

    possible_cur += size
    if current[0] < possible_cur:
        current[0] = possible_cur

with open(file, "w") as f:
    f.write(server_version)
    
