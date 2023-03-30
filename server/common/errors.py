class ProtocolViolation(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message


class PacketTooLargeError(Exception):
    def __init__(self, max_bytes: int, packet_length: int):
        self.message = f"Packet too large. Max bytes: {max_bytes} bytes, packet length: {packet_length} bytes"

    def __str__(self):
        return self.message


class InvalidPacketTypeError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return self.message
