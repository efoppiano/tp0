# TP0 - Sistemas Distribuidos I


## Tabla de contenidos

* [Enunciado](#enunciado)
* [Ejecución de los ejercicios](#ejecución-de-los-ejercicios)
  * [Ejercicio 1](#ejercicio-1)
  * [Ejercicio 1.1](#ejercicio-11)
  * [Ejercicio 2](#ejercicio-2)
  * [Ejercicio 3](#ejercicio-3)
  * [Ejercicio 4](#ejercicio-4)
  * [Ejercicio 5](#ejercicio-5)
* [Configuración](#configuración)
  * [Configuración de los clientes](#configuración-de-los-clientes)
  * [Configuración de los servidores](#configuración-de-los-servidores)
* [Protocolo de comunicación cliente-servidor](#protocolo-de-comunicacin-cliente-servidor)
  * [Tamaño del paquete](#tamaño-del-paquete)
  * [Codificación de los paquetes](#codificación-de-los-paquetes)
  * [Tipo de paquete](#tipo-de-paquete)
  * [Paquetes](#paquetes)
    * [StoreBet](#storebet)
    * [StoreResponse](#storeresponse)


## Enunciado
[Link al enunciado](enunciado.md)

## Ejecución de los ejercicios

### Ejercicio 1

Para verificar que se agregó un nuevo cliente al proyecto, ejecutar:

    $> make docker-compose-up

Al finalizar, se espera un output similar al siguiente:
```bash
[+] Running 3/3
 ⠿ Container server   Started                                0.7s
 ⠿ Container client2  Started                                1.1s
 ⠿ Container client1  Started                                1.1s
```

### Ejercicio 1.1

Correr el script con el siguiente comando:

    $> python3 scripts/write_compose.py <NUMBER_OF_CLIENTS>

### Ejercicio 2

Para verificar que funcionan los volúmenes, ejecutar:

    $> make docker-compose-up

Modificar el archivo `server/config.ini`. Luego, ingresar en el container del servidor y confirmar
que el archivo fue modificado:

    $> docker exec -it server bash
    $> cat config.ini

### Ejercicio 3

El siguiente comando levanta los containers y envía dos mensajes al servidor, utilizando netcat:

    $> make RERUN=1 test-netcat-auto

Se espera el siguiente output:

```bash
docker exec netcat sh -c "echo 'Hello World!' | nc server 12345"
Hello World!
docker exec netcat sh -c "echo 'Elian Foppiano' | nc server 12345"
Elian Foppiano
```

Para enviar mensajes manualmente, ejecutar:

    $> make RERUN=1 test-netcat-manual
    $> echo 'Mensaje' | nc server 12345


### Ejercicio 4

Ejecutar:

    $> make docker-compose-up
    $> make docker-compose-stop
    $> docker compose -f docker-compose-dev.yaml logs | grep "shutdown "

Y confirmar que todos los containers se detuvieron correctamente.

### Ejercicio 5

Ejecutar:

    $> make docker-compose-up
    $> docker compose -f docker-compose-dev.yaml logs | grep apuesta_enviada
    $> docker compose -f docker-compose-dev.yaml logs | grep apuesta_almacenada


## Configuración

### Configuración de los clientes

Los clientes se configuran en el archivo [client/config.yaml](./client/config.yaml).

- `server.address`: Dirección y puerto del servidor al cual se conecta el cliente.
- `log.level`: Nivel de log. Puede ser `debug`, `info`, `warn`, `error` o `fatal`.

### Configuración de los servidores

Los servidores se configuran en el archivo [server/config.ini](./server/config.ini).

- `SERVER_LISTEN_BACKLOG`: Cantidad de conexiones pendientes que se pueden mantener en la cola de
espera.

- `LOGGING_LEVEL`: Nivel de log. Puede ser `NOTSET` `DEBUG`, `INFO`, `WARNING`, `ERROR` o `CRITICAL`.


## Protocolo de comunicación cliente-servidor

### Tamaño del paquete

Los primeros 2 bytes de cada paquete indican el tamaño del paquete en bytes, sin contar estos 2 bytes.
Por lo tanto, dicho tamaño debe ser menor o igual a 8190 (8 kB - 2 B).

El tamaño se codifica en formato **big-endian**.

| Bytes                     | Contenido     |
|---------------------------|---------------|
| 0 ... 1                   | Packet Length |
| 2 ... (Packet Length + 1) | Payload       |


### Codificación de los paquetes

El resto del paquete se codifica en formato utf-8.


### Tipo de paquete

El primer segmento de cada paquete es el tipo de paquete, y se separa del resto del paquete con un
carácter `:`.

### Paquetes

#### StoreBet

Es enviado por el cliente al servidor para almacenar una apuesta individual.

El cliente debe esperar recibir un paquete `StoreResponse` antes de enviar cualquier otro paquete.

- Formato (payload): `StoreBet:agencia;nombre;apellido;documento;nacimiento;numero`
- Ejemplo: `StoreBet:1;Juan;Perez;12345678;1980-01-01;1234`

#### StoreResponse

Es enviado por el servidor al cliente para responder a un paquete `StoreBet`.

- Formato (payload): `StoreResponse:status`
- Ejemplo: `StoreResponse:0`

- status == 0: La apuesta se almacenó correctamente.
- status == 1: Hubo un error al almacenar la apuesta.

