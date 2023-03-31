import socket
from threading import Lock, Event
#import tqdm
import threading
import os
import hashlib
import logging
from datetime import datetime
import time

file_handler = ''
logger = ''
def clientHandler(client_socket, lock, evento, espera):
    global numUsers
    global received
    global activosActual 
    global logger
    filename = ''
    numUsers = ''
    
    rol = 0
    lock.acquire()
    while(numUsers != '' and activosActual > int(numUsers) -1):
        lock.release()
        espera.wait()
        lock.acquire()

    if(activosActual == 0):
        activosActual = 1
        rol = 1
        client_socket.send(f"enviar".encode())
        received = client_socket.recv(BUFFER_SIZE).decode()

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
        file_handler = logging.FileHandler('Logs/'+str(dt_string)+'-log.txt')
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        client_socket.send(f"recibir".encode())
        client_socket.recv(8).decode()
        activosActual += 1
    filename, numUsers = received.split(SEPARATOR)
    lock.release()
    filename = "./archivosDisponibles/" + filename
    filesize = os.path.getsize(filename)
    hash = hash_file(filename)
    client_socket.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{hash}".encode())
    client_socket.recv(BUFFER_SIZE).decode()
    cliente =  str(client_socket.getpeername())
    if(activosActual < int(numUsers)):
        evento.wait()
    evento.set()
    evento.clear()
    if( activosActual == int(numUsers)):
        with open(filename, "rb") as f:
            start = time.time()
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.send(bytes_read)  
    print('enviado')
    client_socket.shutdown(socket.SHUT_WR)
    confirmacion = client_socket.recv(BUFFER_SIZE).decode()
    end = time.time()
    if(confirmacion == 'Integridad del archivo verificada'):
        logging.info('Nombre archivo: '+filename+' -Tamano archivo: '+str(filesize) 
                     + '\n' + 'Cliente: ' +cliente 
                     +'\n'  + 'Integridad: ' + confirmacion 
                     + '\n' + 'Tiempo Transferencia: '+str((end-start) * 10**3)
                     +'\n' )
    else:
        logging.warning('Nombre archivo: '+filename+' -Tamano archivo: '+str(filesize) 
                        + '\n' + 'Cliente: ' + cliente 
                        +'\n'  + 'Integridad: ' + confirmacion
                        +'\n' + 'Tiempo Transferencia: '+str((end-start) * 10**3)
                        +'\n' )
    client_socket.close()
    lock.acquire()
    activosActual -= 1
    if(activosActual <= 0 or threading.activeCount() - 1 == 0):
        filename = ''
        numUsers = ''
        activosActual = 0
        received = ''
        if(len(logger.handlers) > 0):
            logger.handlers[0].stream.close()
            logger.removeHandler(logger.handlers[0])
        espera.set()
        espera.clear()
    lock.release()

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


SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

lock = Lock()
evento = Event()
espera = Event()
activosActual = 0
received = ''

s = socket.socket()
s.bind((SERVER_HOST, SERVER_PORT))
s.listen(10)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
print("Waiting for the client to connect... ")

while True:
    # wait for client to connect
    client_socket, address = s.accept()
    print(f"[+] {address} is connected.")
    # create and start a thread to handle the client
    client_handler = threading.Thread(target = clientHandler, args=(client_socket, lock, evento, espera))
    client_handler.start()