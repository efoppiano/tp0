import sys

DOCKER_COMPOSE_PATH = "./docker-compose-dev.yaml"

def get_compose_first_part():
    return """version: '3.9'
name: tp0
services:
  server:
    container_name: server
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      - testing_net
"""


def get_compose_client_part(client_id):
    return """
  client{client_id}:
    container_name: client{client_id}
    image: client:latest
    entrypoint: /client
    environment:
      - CLI_ID={client_id}
      - CLI_LOG_LEVEL=DEBUG
    networks:
      - testing_net
    depends_on:
      - server
""".format(client_id=client_id)


COMPOSE_LAST_PART = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: 172.25.125.0/24
"""


def write_all(file, data):
    chars_written = 0
    while chars_written < len(data):
        chars_written += file.write(data[chars_written:])


def write_docker_compose_file(clients_amount):
    with open(DOCKER_COMPOSE_PATH, "w") as docker_compose_file:
        write_all(docker_compose_file, get_compose_first_part())
        for i in range(1, clients_amount+1):
            write_all(docker_compose_file, get_compose_client_part(i))

        write_all(docker_compose_file, COMPOSE_LAST_PART)


def main():
    if len(sys.argv) < 2:
        print("Error: Not enough arguments provided")
        print("Use: python3 ./write_compose.py <NUMBER_OF_CLIENTS>")
        return

    try:
        clients_amount = int(sys.argv[1])
    except ValueError:
        print("Error: Invalid argument provided")
        print("Use: python3 ./write_compose.py <NUMBER_OF_CLIENTS>")
        return
    write_docker_compose_file(clients_amount)

main()
