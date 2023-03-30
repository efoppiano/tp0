# TP0 - Sistemas Distribuidos I


## Tabla de contenidos

* [Enunciado](#enunciado)
* [Ejecución de los ejercicios](#ejecución-de-los-ejercicios)
  * [Ejercicio 1](#ejercicio-1)
  * [Ejercicio 1.1](#ejercicio-11)
  * [Ejercicio 2](#ejercicio-2)

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