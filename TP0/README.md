La entrega fue sobre ed10155346dcf984a6a2cca809a6c594ba634888. Correcciones de los docentes:

    Ejercicio 1: Correcto.
    Ejercicio 1.1: Correcto. Muy complejo hacer comandos de concatenación en Makefile. Es preferible utilizar una librería de templates como Jinja.
    Ejercicio 2: Correcto. Está bien implementado el volume en docker-compose pero no era necesario mover los archivos de config dentro de otro directorio. Se podría haber bindeado los archivos individualmente, por nombre completo. Más aún, es necesario excluir los archivos del COPY que se realiza en el Dockerfile. Pensar que al realizar el COPY se invalida el caché cada vez que el archivo en cuestión se modifica y se incluye una copia dentro de la imagen. Esto no es necesario si el planteo es montar el file que puede recibir cambios en cualquier etapa del desarrollo.
    Ejercicio 3: Con errores. El script utilizado para ejecutar el netcat tiene harcodeado el texto a enviar y el puerto. Estos datos deberían ser pasados por variables. Además, emplea un profile de test en docker-compose pero no lo especifica a la hora de ejecutar el docker-compose run dentro del makefile
    Ejercicio 4: Correcto. Es preferible llamar al atributo _running ya que es una variable privada del objeto. Además, es preferible colocar la invocación del close() más cerca del punto donde se realiza la creación del socket. Por ejemplo mover el bind y listen dentro del run() y luego de salir del bucle colocar el close() para que se vea la simetría. En cualquier caso la implementación elegida funciona perfecto. 
    Ejercicio 5: Correcto. Realiza dos implementaciones: con threads y con procesos. En este caso de mucho procesamiento de wait for I/O ambas funcionarían pero preferír siempre multiprocessing en python. Cuidado con lanzar hilos sin controlar la cantidad, un atacante puede generar rápidamente un DOS si conoce cómo está implementado el código del server. Como agregado, la lista de hilos/procesos únicamente se limpia y vacía al finalizar por completo el bucle de aceptación. Esto podría no ocurrir nunca si el servidor funciona en consecutivo durante meses generando un aumento progresivo en memoria utilizada con posterior caída del sistema.


# Docker Compose Init
El siguiente ejemplo es un cliente-servidor el cual corre en containers
con la ayuda de [docker-compose](https://docs.docker.com/compose/). El presente
repositorio es un ejemplo práctico brindado por la cátedra para que los alumnos
tengan un esqueleto básico de cómo armar un proyecto de cero en donde todas
las dependencias del mismo se encuentren encapsuladas en containers.

El cliente (golang) y el servidor (python) fueron desarrollados en diferentes
lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden
convivir en el mismo proyecto con la ayuda de containers.

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que posee encapsulado diferentes comandos
utilizados recurrentemente en el proyecto en forma de targets. Los targets se ejecutan mediante la invocación de:
* **make <target>**

El target principal a utilizar es **docker-compose-up** el cual permite inicializar
el ambiente de desarrollo (buildear docker images del servidor y client, inicializar
la red a utilizar por docker, etc.) y arrancar los containers de las aplicaciones
que componen el proyecto.

Otros targets de utilizar son:
* **docker-compose-down**: Realiza un docker compose stop para detener los containers
asociados al compose y luego realiza un docker compose down para destruir todos los
recursos asociados al proyecto que fueron inicializados durante el **docker-compose-up**
target. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el
disco de la máquina host se llene.
* **docker-compose-logs**: Permite ver los logs actuales del proyecto. Acompañar con grep
para lograr ver mensajes de una aplicación específica dentro del compose
* **docker-image**: Buildea las imágenes a ser utilizadas tanto en el client como el server.
Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para
testear nuevos cambios en las imágenes antes de arrancar el proyecto.
* **build**: Compila la aplicación cliente en la máquina en vez de docker. La compilación
de esta forma es mucho más rápida pero requiere tener el entorno de golang instalado en la
máquina.

### Servidor
El servidor del presente ejemplo es un Echo Server: los mensajes recibidos por el cliente
son devueltos por el servidor. El servidor actual funciona de la siguiente forma:
1. Servidor acepta una nueva conexión
2. Servidor recibe mensaje del cliente y procede a responder el mismo
3. Servidor desconecta al cliente
4. Servidor procede a recibir una conexión nuevamente

Al ejecutar el comando **make docker-compose-up** para comenzar la ejecución del ejemplo y luego
el comando **make docker-compose-logs**, se observan los siguientes logs:

```
efeyuk@Helena:~/Development/docker-compose-init$ make docker-compose-logs
docker-compose -f docker-compose-dev.yaml logs -f
Attaching to client1, server
server     | 2020-04-10 23:10:54 INFO     Proceed to accept new connections
server     | 2020-04-10 23:10:55 INFO     Got connection from ('172.24.125.3', 60392)
server     | 2020-04-10 23:10:55 INFO     Message received from connection ('172.24.125.3', 60392). Msg: b'[CLIENT 1] Message number 1 sent'
server     | 2020-04-10 23:10:55 INFO     Proceed to accept new connections
server     | 2020-04-10 23:11:05 INFO     Got connection from ('172.24.125.3', 60400)
server     | 2020-04-10 23:11:05 INFO     Message received from connection ('172.24.125.3', 60400). Msg: b'[CLIENT 1] Message number 2 sent'
server     | 2020-04-10 23:11:05 INFO     Proceed to accept new connections
server     | 2020-04-10 23:11:15 INFO     Got connection from ('172.24.125.3', 60406)
server     | 2020-04-10 23:11:15 INFO     Message received from connection ('172.24.125.3', 60406). Msg: b'[CLIENT 1] Message number 3 sent'
server     | 2020-04-10 23:11:15 INFO     Proceed to accept new connections
server     | 2020-04-10 23:11:25 INFO     Got connection from ('172.24.125.3', 60410)
server     | 2020-04-10 23:11:25 INFO     Message received from connection ('172.24.125.3', 60410). Msg: b'[CLIENT 1] Message number 4 sent'
server     | 2020-04-10 23:11:25 INFO     Proceed to accept new connections
client1    | time="2020-04-10T23:10:55Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 1 sent'"
client1    | time="2020-04-10T23:11:05Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 2 sent'"
server     | 2020-04-10 23:11:35 INFO     Got connection from ('172.24.125.3', 60412)
client1    | time="2020-04-10T23:11:15Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 3 sent'"
server     | 2020-04-10 23:11:35 INFO     Message received from connection ('172.24.125.3', 60412). Msg: b'[CLIENT 1] Message number 5 sent'
client1    | time="2020-04-10T23:11:25Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 4 sent'"
server     | 2020-04-10 23:11:35 INFO     Proceed to accept new connections
client1    | time="2020-04-10T23:11:35Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 5 sent'"
server     | 2020-04-10 23:11:45 INFO     Got connection from ('172.24.125.3', 60418)
client1    | time="2020-04-10T23:11:45Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 6 sent'"
server     | 2020-04-10 23:11:45 INFO     Message received from connection ('172.24.125.3', 60418). Msg: b'[CLIENT 1] Message number 6 sent'
server     | 2020-04-10 23:11:45 INFO     Proceed to accept new connections
server     | 2020-04-10 23:11:55 INFO     Got connection from ('172.24.125.3', 60420)
server     | 2020-04-10 23:11:55 INFO     Message received from connection ('172.24.125.3', 60420). Msg: b'[CLIENT 1] Message number 7 sent'
client1    | time="2020-04-10T23:11:55Z" level=info msg="[CLIENT 1] Message from server: Your Message has been received: b'[CLIENT 1] Message number 7 sent'"
server     | 2020-04-10 23:11:55 INFO     Proceed to accept new connections
client1    | time="2020-04-10T23:12:05Z" level=info msg="[CLIENT 1] Main loop finished"
client1 exited with code 0
```

# Ejercicios Prácticos
La idea de los siguientes ejercicios prácticos consiste en que los alumnos
se familiaricen con ambientes de desarrollo implementados en docker/docker-compose,
poniendo énfasis en la automatización de cualquier parte del proyecto y la portabilidad
del mismo (evitar que el usuario que emplea el proyecto tenga que instalar otra dependencia
más que docker/docker-compose para correr las aplicaciones).

El alumno debe forkear el presente repositorio en su cuenta de Github personal y crear un branch
por cada uno de los ejercicios que se encuentran a continuación con su correspondiente implementación.

Se recomienda que el alumno realize un fork privado del repositorio. Para realizar un fork privado,
se debe duplicar el repositorio sobre un repositorio privado ya creado. El [siguiente documento](https://help.github.com/en/github/creating-cloning-and-archiving-repositories/duplicating-a-repository) explica como realizar esto.

## Ejercicio N°1:
Modificar la definición del docker-compose para agregar un nuevo cliente al proyecto.

## Ejercicio N°1.1 (Opcional):
Definir un script (en el lenguaje deseado) que permita crear una definición de
docker-compose con cantidad de clientes N.

## Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración
no requiera un nuevo build de las imágenes de Docker para que los mismos sean efectivos. La configuración a 
través del archivo debe ser _injectada_ al ejemplo y persistida afuera del mismo. (Hint: docker volumes)

## Ejercicio N°3:
Crear un script que permita testear el correcto funcionamiento del servidor utilizando el
comando **netcat**. Dado que el servidor es un EchoServer, se debe enviar un mensaje el servidor
y esperar recibir el mismo mensaje enviado.

Netcat no debe ser instalado en la maquina y no se puede exponer puertos del
servidor para realizar la comunicación. (Hint: docker network)

## Ejercicio N°4:
Modificar cliente o servidor (no es necesario modificar ambos) para que el programa termine 
de forma gracefully al recibir la signal SIGTERM. Terminar la aplicación de
forma gracefully implica que todos los sockets y threads/procesos de la aplicación deben 
cerrarse/joinearse antes que el thread de la aplicación principal muera. Loguear mensajes 
en el cierre de cada recurso.(Hint: Verificar que hace el flag -t utilizado en comando docker-compose-down)

## Ejercicio N°5 (Opcional):
Modificar el servidor actual para que el mismo permita procesar mensajes y aceptar nuevas
conexiones en paralelo.

El alumno puede elegir el lenguaje en el cual desarrollar el nuevo código del servidor. Si el
alumno desea realizar las modificaciones en Python, 
[tener en cuenta las limitaciones del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).
