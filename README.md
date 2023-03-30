# TP0 - Sistemas Distribuidos I


## Tabla de contenidos

* [Enunciado](#enunciado)
* [Configuración](#configuración)
  * [Configuración de los clientes](#configuración-de-los-clientes)
  * [Configuración de los servidores](#configuración-de-los-servidores)


## Enunciado
[Link al enunciado](enunciado.md)

## Configuración

### Configuración de los clientes

Los clientes se configuran en el archivo [client/config.yaml](./client/config.yaml).

- `server.address`: Dirección y puerto del servidor al cual se conecta el cliente.

- `batch_size`: Cantidad de apuestas que se pueden enviar al mismo tiempo, en un único mensaje batch. 

- `log.level`: Nivel de log. Puede ser `debug`, `info`, `warn`, `error` o `fatal`.

### Configuración de los servidores

Los servidores se configuran en el archivo [server/config.ini](./server/config.ini).

- `SERVER_LISTEN_BACKLOG`: Cantidad de conexiones pendientes que se pueden mantener en la cola de
espera.

- `AGENCIES_AMOUNT`: Cantidad de agencias que se van a simular. El servidor esperará a que todas
se cierren para realizar el sorteo.

- `LOGGING_LEVEL`: Nivel de log. Puede ser `NOTSET` `DEBUG`, `INFO`, `WARNING`, `ERROR` o `CRITICAL`.


## Protocolo de comunicación cliente-servidor

Todos los paquetes se codifican en formato utf-8 y finalizan con un salto de línea `\n`.

El primer segmento de cada paquete es el tipo de paquete, y se separa del resto del paquete con un
carácter `:`.

### Paquetes

#### StoreBet

Es enviado por el cliente al servidor para almacenar una apuesta individual.

El cliente debe esperar recibir un paquete `StoreResponse` antes de enviar cualquier otro paquete.

- Formato: `StoreBet:agencia;nombre;apellido;documento;nacimiento;numero\n`
- Ejemplo: `StoreBet:1;Juan;Perez;12345678;1980-01-01;1234\n`

#### StoreBatch

Es enviado por el cliente al servidor para almacenar un lote de apuestas.

El cliente debe esperar recibir un paquete `StoreResponse` antes de enviar cualquier otro paquete.

Cada apuesta se separa con un carácter `:`.

- Formato: `StoreBatch:agencia;nombre;apellido;documento;nacimiento;numero:...:nombre;apellido;documento;nacimiento;numero\n`
- Ejemplo: `StoreBatch:1;Juan;Perez;12345678;1980-01-01;5423:Maria;Gomez;87654321;1999-10-25;1234\n`

#### StoreResponse

Es enviado por el servidor al cliente para responder a un paquete `StoreBet` o `StoreBatch`.

- Formato: `StoreResponse:status\n`
- Ejemplo: `StoreResponse:0\n`

- status == 0: La o las apuestas se almacenaron correctamente.
- status == 1: Hubo un error al almacenar la o las apuestas.

#### AgencyCLose

Es enviado por el cliente al servidor para indicar que una agencia cerró.

Una vez enviado, la agencia no puede enviar más apuestas.
El servidor debe esperar recibir un paquete `AgencyClose` de todas las agencias antes de realizar el
sorteo.

- Formato: `AgencyClose:agencia\n`
- Ejemplo: `AgencyClose:1\n`

#### WinnersRequest

Es enviado por el cliente al servidor para solicitar los ganadores del sorteo correspondiente a la
agencia especificada.

Si el sorteo aún no se realizó, el servidor debe esperar a que todas las agencias cierren para
responder este paquete.

- Formato: `WinnersRequest:agencia\n`
- Ejemplo: `WinnersRequest:1\n`

#### WinnersResponse

Es enviado por el servidor al cliente para responder a un paquete `WinnersRequest`.

Contiene los documentos de los ganadores del sorteo correspondiente a la agencia solicitada.

- Formato: `WinnersResponse:documento1;documento2;...;documentoN\n`
- Ejemplo: `WinnersResponse:34054835;38955439\n`