from typing import Set

from common.errors import ProtocolViolation
from common.packets.packet_factory import MAX_PACKET_SIZE, PACKET_LENGTH_FIELD_SIZE

WINNERS_RESPONSE_PACKET_TYPE = "WinnersResponse"


class WinnersResponse:
    def __init__(self, documents: Set[str]):
        self.documents = documents

    def to_bytes(self) -> bytes:
        """
        Encode the packet to be sent to the agency.
        """
        msg = bytearray()
        msg.extend(bytes(WINNERS_RESPONSE_PACKET_TYPE, "utf-8"))
        msg.extend(b':')
        documents = list(self.documents)
        documents = map(lambda x: x.encode("utf-8"), documents)
        msg.extend(b';'.join(documents))

        length = len(msg)
        # I assume it's virtually impossible to have a packet bigger than the max packet size
        # That would mean that there is (roughly) more than 700 winners in a single agency
        if length > MAX_PACKET_SIZE - PACKET_LENGTH_FIELD_SIZE:
            raise ProtocolViolation("Packet size is too big: {}".format(length))

        msg = length.to_bytes(2, byteorder='big') + msg

        return bytes(msg)
