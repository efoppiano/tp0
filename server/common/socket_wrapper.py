import socket


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

    def send(self, data, flags=0):
        raise Exception("Use send_all instead of send to prevent short writes.")

    def recv(self, num_bytes: int):
        raise Exception("Use recv_exact instead of recv to prevent short reads.")

    def __getattr__(self, name):
        return getattr(self._base, name)





