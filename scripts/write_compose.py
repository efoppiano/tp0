import sys

DOCKER_COMPOSE_PATH = "./docker-compose-dev.yaml"

def get_compose_first_part(servers: int):
    return """version: '3.9'
name: tp0
services:
  server:
    image: server:latest
    entrypoint: python3 /main.py
    environment:
      - PYTHONUNBUFFERED=1
      - LOGGING_LEVEL=DEBUG
    networks:
      testing_net:
        aliases:
          - server
    volumes:
      - ./server/config.ini:/config.ini:ro
      - ./server/shared-volume:/shared-volume
    deploy:
      replicas: {servers}
""".format(servers=servers)


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
    volumes:
      - ./client/config.yaml:/config.yaml
      - .data:/data:ro
""".format(client_id=client_id)


COMPOSE_LAST_PART = """
networks:
  testing_net:
    ipam:
      driver: default
      config:
        - subnet: ${DOCKER_SUBNET}
"""


def write_all(file, data):
    chars_written = 0
    while chars_written < len(data):
        chars_written += file.write(data[chars_written:])


def write_docker_compose_file(clients_amount, servers_amount):
    with open(DOCKER_COMPOSE_PATH, "w") as docker_compose_file:
        write_all(docker_compose_file, get_compose_first_part(servers_amount))
        for i in range(1, clients_amount+1):
            write_all(docker_compose_file, get_compose_client_part(i))

        write_all(docker_compose_file, COMPOSE_LAST_PART)


def main():
    if len(sys.argv) < 3:
        print("Error: Not enough arguments provided")
        print("Use: python3 ./write_compose.py <NUMBER_OF_CLIENTS> <NUMBER_OF_SERVERS>")
        return

    try:
        clients_amount = int(sys.argv[1])
        servers_amount = int(sys.argv[2])
    except ValueError:
        print("Error: Invalid argument provided")
        print("Use: python3 ./write_compose.py <NUMBER_OF_CLIENTS> <NUMBER_OF_SERVERS>")
        return
    write_docker_compose_file(clients_amount, servers_amount)

main()
