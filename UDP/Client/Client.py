import socket
import os
import threading
import time
from datetime import datetime


# Constantes SEPARATOR, BUFFER_SIZE, HOST y PORT
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
BUFFER_SIZE_UDP = 30000
HOST = '192.168.152.131'
PORT = 9879
PORT_UDP = 12000


contador = 0

def correr_clientes(ClientSocket, ClientSocketUDP, ServerAddress):
    global contador 
    contador+=1

    start_time = datetime.now()


    try:
        ClientSocket.connect((HOST, PORT))
        mensaje = "listo"
        ClientSocket.send(str.encode(mensaje))
        # Enviar el número de clientes al servidor
        received = ClientSocket.recv(BUFFER_SIZE).decode()

        filename, filesize = received.split(SEPARATOR)
        filename = os.path.basename(filename)
        filesize = int(filesize)

        sent = ClientSocketUDP.sendto(b"Empezar", ServerAddress)

        with open( "./Client/ArchivosRecibidos/"+filename, "wb") as f:
            while True:
                #print("2.1")
                bytes_read, address = ClientSocketUDP.recvfrom(BUFFER_SIZE_UDP)
                ClientSocketUDP.settimeout(60)
                f.write(bytes_read)

        

    except socket.error as e:
        finish_time = datetime.now()
        tiempo = finish_time - start_time
        write_log_file(filename, filesize, "No se entrega el archivo exitosamente", tiempo )

        print("Un thread ha acabado:" + str(e))
        # Cerrar la conexion del socket
        ClientSocketUDP.close()
        ClientSocket.close()

    
# Ingresar el numero de clientes a establecer conexion
numClientes = int(input("Ingrese el número de clientes: "))
# Contador del numero de threads local para el while
ThreadCount = 0

# Creacion de sockets asociados a los threads y iniciar el metodo correr_cliente de cada thread
while ThreadCount < numClientes:
    # Creacion del socket TCP
    Client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Creacion del socket UDP
    ClientUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (HOST, PORT_UDP)

    # Creacion de los threads
    threading.Thread(target=correr_clientes, args=(Client, ClientUDP, server_address, )).start()

    # Cambiar de puerto para el otro socket UDP
    PORT_UDP = PORT_UDP + 1
    time.sleep(1)
    ThreadCount += 1
    print("Numero del Thread: " + str(ThreadCount))

def write_log_file (file_name, file_size, status_file,time):
    today = datetime.now()
    name_file = str(today.year) + "-" + str(today.month) + "-" + str(today.day) + "-" + str(today.hour) + "-" + str(today.minute) + "-" + str(today.second) + "-" + str(today.microsecond) + str(file_name[7:8]) + "-log.txt"
    log_file = open("./Client/Logs/" + name_file, "w")
    log_file.write("Nombre del archivo: " + file_name + "\n")
    log_file.write("Tamanio del archivo: " + str((os.path.getsize("./Client/ArchivosRecibidos/"+file_name))) + "\n")
    log_file.write("Cliente que recibe la transeferencia de archivos: " + str(file_name[7:8]) + "\n")
    log_file.write("Estado de entrega del archivo: " + str(status_file) + "\n")
    log_file.write("Tiempo de transferencia: " + str(time) + "\n")
    log_file.write("Valor total de bytes enviado: " + str(int(file_size)) + "\n")