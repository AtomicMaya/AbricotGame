# coding=utf-8
import sqlite3
import os
import os.path
import hashlib
import time
import requests
from ftp import *
import socket
from threading import Thread, Timer
from tkinter import *
from tkinter import ttk


def connect():
    r = requests.post(site + "/login.php",
                      data={"pseudo": pseudo.get(), "mdp": hashlib.sha512(password.get().encode()).hexdigest()})
    string = r.text
    if not string.startswith("0x"):
        token = string
        # os.system("")#Chemin vers python local + chemin vers client
        print(token)
    else:
        print(string[3:])


def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def maj():
    ftp.download_file(os.getcwd(), '', "table.sq3", "temp")

    # Gestion de la table
    conection = sqlite3.connect("temp/table.sq3")
    cursor = conection.cursor()
    cursor.execute("SELECT * FROM files")
    data = list(cursor)

    # Taille totale
    global total
    total = [sum([i[3] for i in data])]

    window.after(50, drawProgress)

    def speed(current, total, interval):
        temp = current[0]
        l = []
        while current != total:
            last_sec = round((current[0] - temp) / 1024, 2)
            l.append(last_sec)
            moyenne = sum(l[-10:]) / 10
            print("\r", round(moyenne, 2),
                  "ko/s (ETA: %d seconds)" % int((total[0] - current[0]) / (moyenne * 1024 + 1)),
                  "   DEBUG:current %d" % current[0], end="")
            eta.config(text=(str(int((total[0] - current[0]) / (moyenne * 1024 + 1))) + " s"))
            spee.config(text=(str(int(moyenne)) + " ko/s"))
            temp = current[0]
            time.sleep(interval)

    thread = Thread(None, speed, args=[current, total, 1])
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
            except OSError as exc:  # Guard against race condition
                print("error :", exc)
            ftp.download_file(os.getcwd(), 'data' + path, name, monitoring_var=current)
        elif os.path.isfile(os.path.join(temp_path, name)):
            if md5(os.path.join(temp_path, name)) != Hash:
                ftp.download_file(os.getcwd(), 'data' + path, name, monitoring_var=current)
        else:
            ftp.download_file(os.getcwd(), 'data' + path, name, monitoring_var=current)
        global possible_cur
        possible_cur += size
        if current[0] < possible_cur:
            current[0] = possible_cur

    with open(file, "w") as f:
        f.write(server_version)
    button.config(state=NORMAL)
    clean()


def drawProgress():
    temp = (current[0] / total[0]) * 100
    progressBar["value"] = temp
    rounded = str(int(temp))
    percent.config(text=(rounded + "%"))
    remaining.config(text=(str(int((total[0] - current[0]) / 1024 ** 2))) + " Mo")
    window.after(50, drawProgress)


def clean():
    eta.place_forget()
    remaining.place_forget()
    spee.place_forget()
    explanations.place_forget()


# Determine la version actuelle
file = "RELEASE.manifest"
exist = os.path.isfile("RELEASE.manifest")
if exist:
    f = open(file)
    version = f.read()
    f.close()
else:
    version = 0

# Fenetre
### Va changer prochainement
window = Tk()

Label(window, text="Abricot Game").place(relx=0.5, rely=0.05, anchor=CENTER)
pseudo = StringVar()
password = StringVar()
Label(window, text="Pseudo :").place(relx=0.12, rely=0.2, anchor=CENTER)
Entry(window, textvariable=pseudo, width=20).place(relx=0.6, rely=0.2, anchor=CENTER)
Label(window, text="Password :").place(relx=0.15, rely=0.4, anchor=CENTER)
Entry(window, textvariable=password, width=20, show="*").place(relx=0.6, rely=0.4, anchor=CENTER)
progressBar = ttk.Progressbar(window, orient="horizontal", length=200, mode="determinate")
progressBar.place(relx=0.5, rely=.95, anchor=CENTER)
progressBar["maximum"] = 100
progressBar["value"] = 0
button = Button(window, text="Connect", command=connect)
button.place(relx=0.5, rely=0.55, anchor=CENTER)
button.config(state=DISABLED)
percent = Label(window, text="0%")
percent.place(relx=0.5, rely=0.95, anchor=CENTER)
eta = Label(window, text="inf s")
eta.place(relx=0.8, rely=0.82, anchor=CENTER)
remaining = Label(window, text="X Mo")
remaining.place(relx=0.2, rely=0.82, anchor=CENTER)
spee = Label(window, text="X ko/s")
spee.place(relx=0.5, rely=0.82, anchor=CENTER)
explanations = Label(window, text="Remaining         Speed         ETA")
explanations.place(relx=0.43, rely=0.72, anchor=CENTER)

# Données statiques
server_version = 0
site = "http://abricot.zapto.org:8080"
temp = requests.get(site + "/versions.html")
server_version = temp.json()[0]
update_server_ip = "abricot.zapto.org"

# Créé le client ftp
ftp = Ftp_client(update_server_ip, 21, "user", "123", 1)

# Taille déjà téléchargée
total = 1
current = [0]
possible_cur = 0

# Compare a la version serveur
if version != server_version:
    # maj()

    thread = Thread(None, maj)
    thread.daemon = True
    thread.start()
else:
    progressBar["value"] = 100
    button.config(state=NORMAL)
    percent.config(text="100%")
    clean()

window.mainloop()
