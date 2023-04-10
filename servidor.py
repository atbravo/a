import socket
from threading import Lock, Event
import threading
import os
import hashlib
import logging
from datetime import datetime
import time


#Funcion para manejar cada cliente, se llama una vez por cada cliente conectado
def clientHandler(client_socket, lock, evento, espera):
    global numUsers
    global received
    global activosActual 
    global logger
    filename = ''
    numUsers = ''
    
    #Revisa si el cliente es el primero en conectarse o ya hay alguien conectado
    lock.acquire()
    #Primer caso: El servidor esta lleno
    while(numUsers != '' and activosActual > int(numUsers) -1):
        lock.release()
        espera.wait()
        lock.acquire()
    #Segundo caso: El servidor esta vacio
    if(activosActual == 0):
        activosActual = 1
        client_socket.send(f"enviar".encode())
        received = client_socket.recv(BUFFER_SIZE).decode()

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d-%H-%M-%S")
        file_handler = logging.FileHandler('Logs/'+str(dt_string)+'-log.txt')
        logger = logging.getLogger()
        logger.addHandler(file_handler)
        logging.getLogger().setLevel(logging.DEBUG)
    #Tercer caso: Ya hay alguien conectado pero aun hay cupo
    else:
        client_socket.send(f"recibir".encode())
        client_socket.recv(8).decode()
        activosActual += 1
    filename, numUsers = received.split(SEPARATOR)
    lock.release()

    #Se busca el archivo solicitado y se envia al cliente el nombre del archivo, su tamanio y el hash
    filename = "./archivosDisponibles/" + filename
    filesize = os.path.getsize(filename)
    hash = hash_file(filename)
    client_socket.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{hash}".encode())
    client_socket.recv(BUFFER_SIZE).decode()

    #Guardamos informacion del cliente actual
    cliente =  str(client_socket.getpeername())

    #Espera a que el numero de clientes solicitados este conectado antes de enviar el archivo
    if(activosActual < int(numUsers)):
        evento.wait()
    evento.set()
    evento.clear()
    #Una vez se conectan todos los clientes, se envia el archivo
    if( activosActual == int(numUsers)):
        with open(filename, "rb") as f:
            #Inicia a contar el tiempo de transferencia
            start = time.time()
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_socket.send(bytes_read)  
    print('enviado')
    client_socket.shutdown(socket.SHUT_WR)
    
    #Recibir confirmacion de que se recibio correctamente el archivo
    confirmacion = client_socket.recv(BUFFER_SIZE).decode()
    #Para el cronometro de tiempo de transferencia
    end = time.time()

    #Crea una entrada en el log segun la confirmacion recibida
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
    #Cierra el socket
    client_socket.close()

    #Reinicia los valores del servidor vacio para notificar a los usuarios en espera
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

#Funcion para calcular el hash de un documento
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


SERVER_HOST = "0.0.0.0"
#Puerto por el que se escuchan las conecciones
SERVER_PORT = 8001
#Tamaño de paquetes
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

lock = Lock()
evento = Event()
espera = Event()
activosActual = 0
received = ''

file_handler = ''
logger = ''

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