import socket
import threading
import os
import hashlib
import logging
from datetime import datetime
import time

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")

logging.basicConfig(filename='Logs/'+str(dt_string)+'-log.txt', filemode='w')
logging.getLogger().setLevel(logging.DEBUG)

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
host = "192.168.232.128"
port = 8001
filename = ''
numRec=0

def hash_file(filename):
   h = hashlib.sha1()
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

def conectar(i):
    global numRec
    s2 = socket.socket()

    print(f"[+] Connecting to {host}:{port}")
    s2.connect((host, port))
    print("[+] Connected to ", host)

    rol = s2.recv(BUFFER_SIZE).decode()
    if (rol == 'enviar'):
        filename = input('Archivo a transferir')
        numRec = input('Numero de personas')
        s2.send(f"{filename}{SEPARATOR}{numRec}".encode())
    elif (rol == 'recibir'):
        s2.send(b"ready")

    received = s2.recv(BUFFER_SIZE).decode()
    filename, filesize, hash = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    logging.info('Nombre archivo: '+filename+' -Tamano archivo: '+filesize)
    logging.info('Cliente: '+str(i) + ' conectado')
    filename = './ArchivosRecibidos/'+str(i)+'-Prueba-'+str(numRec)+'.txt'
    filesize = int(filesize)
    s2.send(b"ready")
    with open(filename, "wb") as f:
        start = time.time()
        print('Empieza: '+str(start)+' -Cliente:'+str(i))
        while True:
            bytes_read = s2.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
        end = time.time()
        print('Termina: '+str(end)+' -Cliente:'+str(i))
        logging.info('Tiempo del cliente '+str(i)+': '+str((end-start) * 10**3))

    message = hash_file(filename)
    if (message == hash):
        s2.send(f"Integridad del archivo verificada".encode())
        logging.info('Estado archivo del cliente '+str(i)+': Integridad del archivo verificada')
    else:
        s2.send(f" Integridad del archivo vulnerada".encode())
        logging.warning('Estado archivo del cliente '+str(i)+': ¡¡¡¡Integridad del archivo no se asegura!!!!')
    s2.close()

for i in range(10):
    x = threading.Thread(target = conectar, args=(i,))
    x.start()