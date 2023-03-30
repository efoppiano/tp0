import socket

from common.errors import PacketTooLargeError


class SocketWrapper:
    """
    Wrapper of socket.socket that provides additional functionality,
    such as sending all data or receiving exact number of bytes,
    to prevent short reads and writes.
    """
    def __init__(self, base: socket.socket):
        self._base = base

    def send_all(self, data, flags=0):
        bytes_send = 0
        while bytes_send < len(data):
            bytes_send += self._base.send(data, flags)

    def recv_exact(self, num_bytes: int):
        data = b''
        while len(data) < num_bytes:
            data += self._base.recv(num_bytes - len(data))
        return data

    def recv_until(self, delimiter: bytes):
        data = b''
        while not data.endswith(delimiter):
            data += self._base.recv(1)
        return data

    def recv_until_with_max(self, delimiter: bytes, max_bytes: int):
        data = b''
        while not data.endswith(delimiter) and len(data) < max_bytes:
            data += self._base.recv(1)

        if len(data) == max_bytes and not data.endswith(delimiter):
            raise PacketTooLargeError()
        return data

    def __getattr__(self, name):
        return getattr(self._base, name)





