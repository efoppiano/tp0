import socket
import logging
from typing import Set

from common.socket_wrapper import SocketWrapper

from common.packets.packet_factory import PacketFactory

from common.errors import ProtocolViolation
from common.packets.store_response import StoreResponse, STATUS_ERROR, STATUS_OK
from common.utils import store_bets

from common.ipc.closed_agencies import ClosedAgencies
from common.packets.winners_response import WinnersResponse
from common.utils import load_bets, has_won

from common.packets.not_ready_response import NotReadyResponse


class ServerConfig:
    def __init__(self, logging_level, port, listen_backlog, agencies_amount):
        self.logging_level = logging_level
        self.port = port
        self.listen_backlog = listen_backlog
        self.agencies_amount = agencies_amount

class Server:
    def __init__(self, config: ServerConfig):
        self._config = config

        self._closed_agencies = ClosedAgencies()

        # When the bet ends, this will contain a dictionary with the winners per agency.
        # The key will be the agency number and the value will be a list of the documents
        # of the winners.
        self._winners_per_agency = None

        self.__set_up_tcp_socket()
        self._client_sock = None

    def __set_up_tcp_socket(self):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self._server_socket.bind(('', self._config.port))
        self._server_socket.listen(self._config.listen_backlog)

    def __bet_ended(self) -> bool:
        return len(self._closed_agencies.get_closed_agencies()) == self._config.agencies_amount

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
        self._client_sock = client_sock
        addr = client_sock.getpeername()
        try:
            self.__handle_packet(client_sock)
            client_sock.close()
            self._client_sock = None
            logging.info(f'action: client_disconnection | result: success | ip: {addr[0]}')
        except Exception as e:
            logging.error(f"action: receive_message | result: fail | ip: {addr[0]} | error: {e}")
            client_sock.close()
            self._client_sock = None
            logging.info(f'action: client_disconnection | result: success | ip: {addr[0]}')

    def __handle_packet(self, client_sock: SocketWrapper):
        """
        Handles a packet received from a client.
        Returns True if the socket should be closed, False otherwise.
        """
        data = PacketFactory.read_raw_packet(client_sock)
        if PacketFactory.is_for_store_bet(data):
            self.__handle_store_bet(client_sock, data)
        elif PacketFactory.is_for_store_batch(data):
            self.__handle_store_batch(client_sock, data)
        elif PacketFactory.is_for_agency_close(data):
            self.__handle_agency_close(data)
        elif PacketFactory.is_for_winners_request(data):
            self.__handle_winners_request(client_sock, data)
        else:
            raise ProtocolViolation(f"Invalid packet type ({PacketFactory.get_packet_type(data)})")

    def __handle_store_bet(self, client_sock: SocketWrapper, data: bytes):
        try:
            bet = PacketFactory.parse_store_bet_packet(data)
            # Cannot store bets for closed agencies.
            if self._closed_agencies.contains(bet.agency):
                client_sock.send_all(StoreResponse(STATUS_ERROR).to_bytes())
                return
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
            # Cannot store bets for closed agencies.
            agency = bets[0].agency
            if self._closed_agencies.contains(agency):
                client_sock.send_all(StoreResponse(STATUS_ERROR).to_bytes())
                return
            store_bets(bets)

            logging.info(f'action: apuestas_almacenadas | result: success | cantidad: {len(bets)}')
            client_sock.send_all(StoreResponse(STATUS_OK).to_bytes())
        except Exception as e:
            logging.error(f"action: parse_store_batch_packet | result: fail | error: {e}")
            client_sock.send_all(StoreResponse(STATUS_ERROR).to_bytes())

    def __handle_agency_close(self, data: bytes):
        agency = PacketFactory.parse_agency_close_packet(data)
        logging.info(f'action: agency_close | result: in_progress | agency: {agency}')
        self._closed_agencies.add(int(agency))
        logging.info(f'action: agency_close | result: success | agency: {agency}')

    def __populate_winners(self):
        logging.info('action: populate_winners | result: in_progress')
        self._winners_per_agency = {}
        for bet in load_bets():
            if has_won(bet):
                self._winners_per_agency.setdefault(bet.agency, [])
                self._winners_per_agency[bet.agency].append(bet.document)

        logging.info(f'action: populate_winners | result: success | winners: {self._winners_per_agency}')

    def __get_winners_of_agency(self, agency: int) -> Set[str]:
        if self._winners_per_agency is None:
            logging.info(f'action: get_winners_of_agency | result: in_progress | agency: {agency}')
            self.__populate_winners()

        return self._winners_per_agency.get(agency, set())

    def __send_winners(self, client_sock: SocketWrapper, agency: str):
        winners_of_agency = self.__get_winners_of_agency(int(agency))
        winners_packet = WinnersResponse(winners_of_agency)

        client_sock.send_all(winners_packet.to_bytes())
        logging.info(f'action: send_winners | result: success | agency: {agency} | winners: {len(winners_of_agency)}')

    def __handle_winners_request(self, client_sock: SocketWrapper, data: bytes) -> bool:
        """
        Handle winners request from an agency
        If all agencies have closed, send winners to agency immediately, returning True
        Otherwise, add agency to waiting list and return False
        """
        agency = PacketFactory.parse_winners_request_packet(data)

        closed_agencies = self._closed_agencies.get_closed_agencies()
        if len(closed_agencies) != self._config.agencies_amount:
            logging.info(
                f'action: send_winners | result: delayed | agency: {agency} | closed_agencies: {closed_agencies}')
            client_sock.send_all(NotReadyResponse().to_bytes())
        else:
            logging.info(f'action: send_winners | result: in_progress | agency: {agency}')
            self.__send_winners(client_sock, agency)

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

