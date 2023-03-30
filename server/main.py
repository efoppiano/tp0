#!/usr/bin/env python3

import os
import logging
import signal
import sys
from configparser import ConfigParser
from common.server import Server, ServerConfig


def initialize_config():
    """ Parse env variables or config file to find program config params

    Function that search and parse program configuration parameters in the
    program environment variables first and the in a config file. 
    If at least one of the config parameters is not found a KeyError exception 
    is thrown. If a parameter could not be parsed, a ValueError is thrown. 
    If parsing succeeded, the function returns a ConfigParser object 
    with config parameters
    """

    config = ConfigParser(os.environ)
    # If config.ini does not exists original config object is not modified
    config.read("config.ini")

    config_params = {}
    try:
        config_params["port"] = int(os.getenv('SERVER_PORT', config["DEFAULT"]["SERVER_PORT"]))
        config_params["listen_backlog"] = int(os.getenv('SERVER_LISTEN_BACKLOG', config["DEFAULT"]["SERVER_LISTEN_BACKLOG"]))
        config_params["logging_level"] = os.getenv('LOGGING_LEVEL', config["DEFAULT"]["LOGGING_LEVEL"])
        config_params["agencies_amount"] = int(os.getenv('AGENCIES_AMOUNT', config["DEFAULT"]["AGENCIES_AMOUNT"]))
    except KeyError as e:
        raise KeyError("Key was not found. Error: {} .Aborting server".format(e))
    except ValueError as e:
        raise ValueError("Key could not be parsed. Error: {}. Aborting server".format(e))

    return ServerConfig(**config_params)


def main():
    server_config = initialize_config()

    initialize_log(server_config.logging_level)

    # Log config parameters at the beginning of the program to verify the configuration
    # of the component
    logging.debug(f"action: config | result: success | port: {server_config.port} | "
                  f"listen_backlog: {server_config.listen_backlog} | logging_level: {server_config.logging_level} | "
                  f"agencies_amount: {server_config.agencies_amount}")

    # Initialize server and start server loop
    server = Server(server_config)

    def shutdown_handler(_signum, _frame):
        server.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, shutdown_handler)
    server.run()


def initialize_log(logging_level):
    """
    Python custom logging initialization

    Current timestamp is added to be able to identify in docker
    compose logs the date when the log has arrived
    """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging_level,
        datefmt='%Y-%m-%d %H:%M:%S',
    )


if __name__ == "__main__":
    main()
