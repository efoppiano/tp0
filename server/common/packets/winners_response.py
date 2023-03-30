from typing import Set

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

        msg.extend(b'\n')
        return bytes(msg)
