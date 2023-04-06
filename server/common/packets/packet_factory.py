import logging

from common.packets.store_bet import StoreBet, STORE_BET_PACKET_TYPE
from common.socket_wrapper import SocketWrapper
from common.utils import Bet

from common.errors import InvalidPacketTypeError

from common.errors import ProtocolViolation

MAX_PACKET_SIZE = 8192
PACKET_LENGTH_FIELD_SIZE = 2


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
    def read_raw_packet(socket: SocketWrapper) -> bytes:
        """
        Read raw packet from client socket.
        """
        length = int.from_bytes(socket.recv_exact(2), byteorder='big')
        if length > MAX_PACKET_SIZE - PACKET_LENGTH_FIELD_SIZE:
            raise ProtocolViolation("Packet size exceeds maximum packet size.")

        data = socket.recv_exact(length)
        addr = socket.getpeername()

        logging.info(f'action: read_raw_packet | result: success | ip: {addr[0]} | msg: {data}')

        return data

    @staticmethod
    def is_for_store_bet(data: bytes) -> bool:
        return PacketFactory.__check_packet_type(data, STORE_BET_PACKET_TYPE)

    @staticmethod
    def __check_packet_type(data: bytes, expected_type: str) -> bool:
        packet_type = data[:data.find(b':')].decode("utf-8")
        return packet_type == expected_type
