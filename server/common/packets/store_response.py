STORE_RESPONSE_PACKET_TYPE = "StoreResponse"

STATUS_OK = 0
STATUS_ERROR = 1


class StoreResponse:
    def __init__(self, status: int):
        self.status = status

    def to_bytes(self) -> bytes:
        """
        Encode the packet to be sent to the agency.
        """
        msg = bytearray()
        msg.extend(bytes(STORE_RESPONSE_PACKET_TYPE, "utf-8"))
        msg.extend(b':')
        msg.extend(str(self.status).encode("utf-8"))

        msg = len(msg).to_bytes(2, byteorder='big') + msg

        return bytes(msg)

