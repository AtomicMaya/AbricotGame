import threading
import logging
import ftplib
import socket
import time
import os, os.path

def set_interval(interval, times =-1):
    """
    Decorator with interval and times parameters
    """
    
    def outer_wrap(function):
        # This function to be called

        def wrap(*args, **kwargs):
            stop = threading.Event()
            
            def inner_wrap():
                i = 0
                while i != times and not stop.is_set():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1
            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap

class Ftp_client:
    """
    Objet permettant le téléchargement de fichiers à partir d'un FTP
    """
    def __init__(self, host, port, login, password, monitor_interval=30):
        """
        host = adresse du serveur
        port = port du serveur
        login = nom de connexion du serveur
        password = mot de passe du serveur
        monitor_interval = temps entre le monitoring
        """
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.monitor_interval = monitor_interval
        self.ptr = None
        self.max_attempts = 1
        self.waiting = True

    def download_file(self, act ,path, filename, local_path="", monitoring_var=None):
        """
        Fonction destinée à télécharger un fichier sur le serveur FTP
        act : répertoire courant
        path : chemin relatif du fichier sur le serveur distant
        filename : nom du fichier sur le serveur distant
        local_path : chemin relatif pour le fichier local. Non utilisé pour
        le moment puisque le chemin est identique.
        """
        res = ''
        #Si le chemin vers le fichier n'existe pas, le créé
        if not os.path.exists(path) and not path=="":
            try:
                os.makedirs(path)
            except OSError as exc: # Guard against race condition
                print("error :",exc)
                
        if not os.path.exists(local_path) and not local_path=="":
            try:
                os.makedirs(local_path)
            except OSError as exc: # Guard against race condition
                print("error :",exc)
                
        #Créé un chemin relatif avec le chemin et le nom du fichier
        if local_path:
            local = os.path.join(local_path, filename)
        else:
            local = os.path.join(path, filename)
        complete_path = os.path.join(path, filename)

        #Ecriture du fichier en local
        with open(os.path.join(act, local), "w+b") as f:           
            self.ptr = f.tell()
            #Fonction permettant de monitorer l'état du transfert
            @set_interval(self.monitor_interval)
            def monitor(s=None):
                if not self.waiting:
                    try:
                        i = f.tell()
                        if self.ptr < i:
                            self.ptr = i
                            if monitoring_var:
                                monitoring_var[0] = s + i
                        else:
                            ftp.close()
                    except OSError:
                        pass

            #Connexion au FTP
            def connect():
                ftp.connect(self.host, self.port)
                ftp.login(self.login, self.password)
                ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            ftp = ftplib.FTP()
            #ftp.set_debuglevel(1)
            ftp.set_pasv(False)

            connect()
            ftp.voidcmd('TYPE I')
            file_size = ftp.size(complete_path)

            if monitoring_var:
                s = monitoring_var[0]
                mon = monitor(s)
            else:
                mon = monitor()
                
            #Télécharge tant que le fichier n'est pas complet.
            while file_size > f.tell():
                try:
                    self.waiting = False
                    res = ftp.retrbinary('RETR %s' % complete_path, f.write) if f.tell() == 0 else \
                              ftp.retrbinary('RETR %s' % complete_path, f.write, rest=f.tell())
                except:
                    self.max_attempts -= 1
                    if self.max_attempts == 0:
                        mon.set()
                        logging.exception('')
                        raise
                    self.waiting = True
                    print("wait 1sec")
                    time.sleep(1)
                    print('reconnect')
            mon.set()
            ftp.close()

            return 1



                        
