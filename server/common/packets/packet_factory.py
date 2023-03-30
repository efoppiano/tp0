import logging

from common.packets.store_bet import StoreBet, STORE_BET_PACKET_TYPE
from common.socket_wrapper import SocketWrapper
from common.utils import Bet

from common.errors import InvalidPacketTypeError

from common.packets.store_batch import STORE_BATCH_PACKET_TYPE

from common.packets.store_batch import StoreBatch

from common.packets.agency_close import AGENCY_CLOSE_PACKET_TYPE

from common.packets.agency_close import AgencyClose

from common.packets.winners_request import WINNERS_REQUEST_PACKET_TYPE

from common.packets.winners_request import WinnersRequest
from typing import List

MAX_PACKET_SIZE = 8192


def remove_packet_type(data: bytes) -> bytes:
    return data[data.find(b':') + 1:]


class PacketFactory:
    @staticmethod
    def parse_store_bet_packet(data: bytes) -> Bet:
        """
        Receives a raw packet (result of a PacketFactory.read_raw_packet call) and parses
        it into a Bet object.
        If the packet is not a StoreBet packet, raises an InvalidPacketTypeError.
        """
        if not PacketFactory.is_for_store_bet(data):
            raise InvalidPacketTypeError("Invalid packet type in StoreBet packet (expected 0).")
        data = remove_packet_type(data)
        return StoreBet.parse_bet(data)

    @staticmethod
    def parse_store_batch_packet(data: bytes) -> List[Bet]:
        """
        Receives a raw packet (result of a PacketFactory.read_raw_packet call) and parses
        it into a list of Bet objects.
        If the packet is not a StoreBatch packet, raises an InvalidPacketTypeError.
        """
        if not PacketFactory.is_for_store_batch(data):
            raise InvalidPacketTypeError("Invalid packet type in StoreBatch packet (expected 2).")
        data = remove_packet_type(data)
        return StoreBatch.parse_batch(data)

    @staticmethod
    def parse_agency_close_packet(data: bytes) -> str:
        """
        Receives a raw packet (result of a PacketFactory.read_raw_packet call) and parses
        it into an agency number of the agency that closed.
        If the packet is not an AgencyClose packet, raises an InvalidPacketTypeError.
        """
        if not PacketFactory.is_for_agency_close(data):
            raise InvalidPacketTypeError("Invalid packet type in AgencyClose packet (expected 3).")
        data = remove_packet_type(data)
        return AgencyClose.parse_agency(data)

    @staticmethod
    def parse_winners_request_packet(data: bytes) -> str:
        """
        Receives a raw packet (result of a PacketFactory.read_raw_packet call) and parses
        it into the agency number of the agency that requested the winners.
        """
        if not PacketFactory.is_for_winners_request(data):
            raise InvalidPacketTypeError("Invalid packet type in WinnersRequest packet (expected 4).")
        data = remove_packet_type(data)
        return WinnersRequest.parse_agency(data)

    @staticmethod
    def read_raw_packet(socket: SocketWrapper) -> bytes:
        """
        Read raw packet from client socket.
        """
        data = socket.recv_until_with_max(b'\n', MAX_PACKET_SIZE)
        addr = socket.getpeername()

        logging.info(f'action: read_raw_packet | result: success | ip: {addr[0]} | msg: {data}')

        return data.rstrip(b'\n')

    @staticmethod
    def is_for_store_bet(data: bytes) -> bool:
        return PacketFactory.__check_packet_type(data, STORE_BET_PACKET_TYPE)

    @staticmethod
    def is_for_store_batch(data: bytes) -> bool:
        return PacketFactory.__check_packet_type(data, STORE_BATCH_PACKET_TYPE)

    @staticmethod
    def is_for_agency_close(data: bytes) -> bool:
        return PacketFactory.__check_packet_type(data, AGENCY_CLOSE_PACKET_TYPE)

    @staticmethod
    def is_for_winners_request(data: bytes) -> bool:
        return PacketFactory.__check_packet_type(data, WINNERS_REQUEST_PACKET_TYPE)

    @staticmethod
    def __check_packet_type(data: bytes, expected_type: str) -> bool:
        packet_type = data[:data.find(b':')].decode("utf-8")
        return packet_type == expected_type
