import socket
import threading
import os
import hashlib

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
host = "192.168.1.142"
port = 8001
filename = ''

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

def conectar():
    s2 = socket.socket()

    print(f"[+] Connecting to {host}:{port}")
    s2.connect((host, port))
    print("[+] Connected to ", host)

    rol = s2.recv(BUFFER_SIZE).decode()
    if (rol == 'enviar'):
        filename = input('Archivo a transferir')
        s2.send(f"{filename}".encode())
    else:
        s2.send(b"ready")
    
    received = s2.recv(BUFFER_SIZE).decode()
    filename, filesize, hash = received.split(SEPARATOR)
    filename = os.path.basename(filename)
    print(filename)
    filesize = int(filesize)
    s2.send(b"ready")
    with open(filename, "wb") as f:
        while True:
            bytes_read = s2.recv(BUFFER_SIZE)
            if not bytes_read:
                break
            f.write(bytes_read)

            
    message = hash_file(filename)
    if (message == hash):
        print("Integridad del archivo verificada")
    else:
        print("¡¡¡¡Integridad del acchivo no se asegura!!!!")
    s2.close()

for i in range(5):
    x = threading.Thread(target = conectar, args=())
    x.start()