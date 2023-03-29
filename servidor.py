import socket
#import tqdm
import threading
import os
import hashlib
enviar = 0
def clientHandler(client_socket):
    if(enviar == 0):
        enviar = 1
        client_socket.send(f"enviar".encode())
        received = client_socket.recv(BUFFER_SIZE).decode()
    else:
        client_socket.send(f"recibir".encode())
        client_socket.recv(8).decode()

    filename = received
    filesize = os.path.getsize(filename)
    hash = hash_file(filename)
    client_socket.send(f"{filename}{SEPARATOR}{filesize}{SEPARATOR}{hash}".encode())
    #file = open(filename, 'wb') 
    client_socket.recv(BUFFER_SIZE).decode()
    #progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "rb") as f:
        while True:
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                break
            client_socket.sendall(bytes_read)
            #progress.update(len(bytes_read))   
    print(threading.activeCount() - 1)
    client_socket.close()

def hash_file(filename):
   h = hashlib.sha1()
   with open(filename,'rb') as file:

       # loop tilxl the end of the file
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
    client_handler = threading.Thread(target = clientHandler, args=(client_socket,))
    client_handler.start()

#s.close()