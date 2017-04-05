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
    def __init__(self, host, port, login, password, monitor_interval=30):
        self.host = host
        self.port = port
        self.login = login
        self.password = password
        self.monitor_interval = monitor_interval
        self.ptr = None
        self.max_attempts = 15
        self.waiting = True

    def download_file(self, act ,path, filename):
        res = ''
        complete_path = os.path.join(path, filename)
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(os.path.join(act, complete_path), "w+b") as f:
            print(f.name)
            self.ptr = f.tell()

            @set_interval(self.monitor_interval)
            def monitor():
                if not self.waiting:
                    i = f.tell()
                    if self.ptr < i:
                        logging.debug('%d  -  %0.1f Kb/s' % (i, (i-self.ptr)/(1024*self.monitor_interval)))
                        print('%d  -  %0.1f Kb/s' % (i, (i-self.ptr)/(1024*self.monitor_interval)))
                        self.ptr = i
                    else:
                        ftp.close()

            def connect():
                ftp.connect(self.host, self.port)
                ftp.login(self.login, self.password)
                ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                #ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 75)
                #ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)

            ftp = ftplib.FTP()
            ftp.set_debuglevel(2)
            ftp.set_pasv(True)

            connect()
            ftp.voidcmd('TYPE I')
            file_size = ftp.size(complete_path)

            mon = monitor()
            while file_size > f.tell():
                try:
                    connect()
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
                    logging.info("wait 30sec")
                    time.sleep(30)
                    logging.info('reconnect')

            mon.set()
            ftp.close()

            return 1

#logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=cfg.logging.level)
obj = Ftp_client('localhost', 21, 'client', '123', 5)
print("CONNEXION EFFECTUEE")
obj.download_file(os.getcwd(), 'cgminer-3.7.2-windows', 'test.txt')


                        
