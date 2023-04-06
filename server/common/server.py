import socket
import logging

from common.socket_wrapper import SocketWrapper

from common.packets.packet_factory import PacketFactory

from common.errors import ProtocolViolation
from common.packets.store_response import StoreResponse, STATUS_ERROR, STATUS_OK
from common.utils import store_bets


class ServerConfig:
    def __init__(self, logging_level, port, listen_backlog):
        self.logging_level = logging_level
        self.port = port
        self.listen_backlog = listen_backlog

class Server:
    def __init__(self, config: ServerConfig):
        self._config = config

        # Initialize server socket
        self.__set_up_tcp_socket()
        self._client_sock = None

    def __set_up_tcp_socket(self):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._server_socket.bind(('', self._config.port))
        self._server_socket.listen(self._config.listen_backlog)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while True:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock: SocketWrapper):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        addr = client_sock.getpeername()
        try:
            should_close = self.__handle_packet(client_sock)
            if should_close:
                client_sock.close()
                logging.info(f'action: client_disconnection | result: success | ip: {addr[0]}')
        except Exception as e:
            logging.error(f"action: receive_message | result: fail | ip: {addr[0]} | error: {e}")
            client_sock.close()
            logging.info(f'action: client_disconnection | result: success | ip: {addr[0]}')

    def __handle_packet(self, client_sock: SocketWrapper) -> bool:
        """
        Handles a packet received from a client.
        Returns True if the socket should be closed, False otherwise.
        """
        data = PacketFactory.read_raw_packet(client_sock)
        if PacketFactory.is_for_store_bet(data):
            self.__handle_store_bet(client_sock, data)
            return True
        elif PacketFactory.is_for_store_batch(data):
            self.__handle_store_batch(client_sock, data)
            return True
        else:
            raise ProtocolViolation("Invalid packet type.")

    def __handle_store_bet(self, client_sock: SocketWrapper, data: bytes):
        try:
            bet = PacketFactory.parse_store_bet_packet(data)
            logging.info("action: store_bet | result: in_progress")
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
            client_sock.send_all(StoreResponse(STATUS_OK).to_bytes())
        except Exception as e:
            logging.error(f"action: parse_store_bet_packet | result: fail | error: {e}")
            client_sock.send_all(StoreResponse(STATUS_ERROR).to_bytes())

    def __handle_store_batch(self, client_sock: SocketWrapper, data: bytes):
        try:
            bets = PacketFactory.parse_store_batch_packet(data)
            store_bets(bets)

            logging.info(f'action: apuestas_almacenadas | result: success | cantidad: {len(bets)}')
            client_sock.send_all(StoreResponse(STATUS_OK).to_bytes())
        except Exception as e:
            logging.error(f"action: parse_store_batch_packet | result: fail | error: {e}")
            client_sock.send_all(StoreResponse(STATUS_ERROR).to_bytes())

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return SocketWrapper(c)

    def shutdown(self):
        """
        Shuts down the server
        """
        logging.info("action: shutdown | result: in_progress")
        self._server_socket.close()
        if self._client_sock is not None:
            self._client_sock.close()
        logging.info("action: shutdown | result: success")

