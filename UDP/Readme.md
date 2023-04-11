# Laboratorio 3 Servicio UDP - Infraestructura de Comunicaciones

## Instrucciones de instalación:

Para poder tener el aplicativo desarrollado en el servidor es necesario primero clonar el repositorio, abrir la carpeta Server y crear la carpeta Logs donde quedarán guardados los registros logs de la transferencia de archivos por cada prueba realizada que contiene los registros para cada conexión recibida en la prueba. Luego, se deben crear los archivos de prueba. En una maquina linux se debe ingresar a la carpeta Server/files y correr los siguientes dos comandos.

`dd if=/dev/zero of=100MB.txt bs=1M count=100`

`dd if=/dev/zero of=250MB.txt bs=1M count=250`

Para usar la aplicación del cliente, es necesario seguir algunos pasos. Primero, hay que clonar el repositorio y luego abrir la carpeta del cliente. Dentro de esta carpeta, es necesario crear dos carpetas: Logs y ArchivosRecibidos. Estas carpetas servirán para guardar los registros de transferencia de archivos y los archivos transferidos a cada cliente, respectivamente. Para hacer más fácil el proceso de creación de estas carpetas, ya han sido creadas previamente y contienen un archivo .dummyfile. Al clonar el proyecto, aparecerán estas carpetas automáticamente.

Si se desea ejecutar la aplicación en modo local, el host es '127.0.0.1' tanto para el cliente como para el servidor. Sin embargo, si se quiere ejecutar la aplicación utilizando un servidor Ubuntu Server 18.04, el host en el servidor es '0.0.0.0' y el host en la máquina Windows donde se ejecutará el cliente es la dirección IP correspondiente al servidor. Para conocer la dirección IP del servidor, se puede utilizar el comando 'ifconfig' en el servidor y luego copiarla en el host del cliente.

## Instrucciones de uso:

Para utilizar el aplicativo, es necesario tener tanto la máquina del cliente como la del servidor en funcionamiento. En la máquina del servidor, se debe acceder a la ruta del proyecto y luego a la carpeta Server. A continuación, se debe ingresar el comando "python3 Server.py" para ejecutar la aplicación. Aparecerán mensajes de notificación para ingresar el número de clientes que se desean conectar y el número del archivo que se va a enviar. Una vez que se hayan ingresado estos datos, el socket TCP del servidor quedará en espera de la conexión de los clientes.

En la máquina del cliente, se debe acceder al proyecto y luego a la carpeta Cliente. Se debe ingresar el comando "python3 Client.py" para ejecutar la aplicación. Aparecerá un mensaje de notificación para ingresar el número de clientes. Una vez que tanto el servidor como el cliente hayan ingresado los datos, se establecerá la conexión y comenzará el servicio de transferencia de archivos, que es compatible con los sockets UDP. Se generarán registros de transferencia de archivos de envío/recepción en cada lado del cliente-servidor y los archivos recibidos por los clientes se almacenarán en la carpeta ArchivosRecibidos.