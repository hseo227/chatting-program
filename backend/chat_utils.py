import socket
import pickle
import struct
import time

# The following types are used to represent each client:
Address = tuple[str, int]
Client = tuple[Address, str, float]
SERVER_HOST = "localhost"


def send(channel: socket.socket, *args) -> None:
    """
    Sends an object to the provided socket.
    """
    buffer: bytes = pickle.dumps(args)
    value: int = socket.htonl(len(buffer))
    size: bytes = struct.pack("L", value)
    channel.send(size)
    channel.send(buffer)


def receive(channel: socket.socket) -> tuple:
    """
    Receives an object from the provided socket.
    """
    size = struct.calcsize("L")
    size = channel.recv(size)
    try:
        size = socket.ntohl(struct.unpack("L", size)[0])
    except struct.error:
        return ()
    buf = ""
    while len(buf) < size:
        buf = channel.recv(size - len(buf))
    return pickle.loads(buf)


def format_message(nickname: str, message: str) -> str:
    """
    Links nickname and message with current time, into single string.
    """
    return f'{nickname} ({time.strftime("%H:%M", time.localtime())}): {message}'
