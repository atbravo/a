import socket
import threading
from threading import Lock
import os
import hashlib
import logging
from datetime import datetime
import time

now = datetime.now()
dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")

#Variables importantes
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
host = "192.168.232.128"
port = 8001
filename = ''
numRec=0
lock = Lock()

def hash_file(filename):
   h = hashlib.sha256()
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

#Funcion que corre cada thread
def conectar(i):
    global lock
    global numRec
    s2 = socket.socket()

    #Se conecta al servidor
    s2.connect((host, port))

    rol = s2.recv(BUFFER_SIZE).decode()

    #Dependiendo del rol del cliente se solicita el nombre del archivo a anviar y el numero de personas 
    #o se le informa al servidor que ya esta listo para recibir el archivo
    if (rol == 'enviar'):
        print('Subimos dos archivos: \'archivo100.txt\', \'archivo250.txt\'')
        filename = input('Escoja el Archivo a transferir ')
        numRec = input('Numero de personas ')
        s2.send(f"{filename}{SEPARATOR}{numRec}".encode())
    elif (rol == 'recibir'):
        s2.send(b"ready")

    #Se recibe informacion importante del servidor como el nombre del archivo, su tamaño y su hash
    received = s2.recv(BUFFER_SIZE).decode()
    filename, filesize, hash = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    #El arvicho se guarda en la carpeta ArchivosRecibidos con la especificaciones presentadas en el
    #enunciado
    filename = './ArchivosRecibidos/'+str(i)+'-Prueba-'+str(numRec)+'.txt'
    filesize = int(filesize)
    s2.send(b"ready")
    #Empieza el envio del archivo pot chunks
    with open(filename, "wb") as f:
        start = time.time()
        while True:
            bytes_read = s2.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)
        end = time.time()
    message = hash_file(filename)

    #Se crea un log por cada cliente con la informacion mas relevante de la conexion de cada uno
    lock.acquire()
    dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
    file_handler = logging.FileHandler('Logs/'+ 'cliente' + str(i) + '-' +str(dt_string)+'-log.txt')
    logger = logging.getLogger()
    logger.addHandler(file_handler)
    logging.getLogger().setLevel(logging.DEBUG)
    logging.info('Nombre archivo: '+filename+' -Tamano archivo: '+ str(filesize) + ' bytes')
    logging.info('Cliente: '+ str(s2.getsockname()) + ' conectado')
    logging.info('Tiempo del cliente '+str(i)+': '+str((end-start) * 10**3) + ' ms')
    if (message == hash):
        s2.send(f"Integridad del archivo verificada".encode())
        logging.info('Estado archivo del cliente '+str(i)+': Integridad del archivo verificada')
    else:
        s2.send(f" Integridad del archivo vulnerada".encode())
        logging.warning('Estado archivo del cliente '+str(i)+': ¡¡¡¡Integridad del archivo no se asegura!!!!')
    logger.handlers[0].stream.close()
    logger.removeHandler(logger.handlers[0])
    lock.release()
    s2.close()

#Creacion de los clientes conectados al servidor, representados a traves de threads que corren la
#funcion principal
for i in range(25):
    x = threading.Thread(target = conectar, args=(i,))
    x.start()