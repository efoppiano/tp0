
NOT_READY_RESPONSE_PACKET_TYPE = "NotReadyResponse"

class NotReadyResponse:
    """
    Packet sent by the server to the client as a response to a WinnersRequest packet,
    when the bet is not ready yet.
    """
    def __init__(self):
        pass

    def to_bytes(self) -> bytes:
        """
        Encode the packet to be sent to the agency.
        """
        msg = bytearray()
        msg.extend(bytes(NOT_READY_RESPONSE_PACKET_TYPE, "utf-8"))
        msg.extend(b':')

        msg = len(msg).to_bytes(2, byteorder='big') + msg

        return bytes(msg)
    