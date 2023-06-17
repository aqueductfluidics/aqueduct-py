"""
The aqueduct.core.socket_helpers module provides various helper functions for working with sockets.

Functions:
- string_to_bool(string: str) -> bool: Convert a string to a boolean value.
- send_and_wait_for_rx(message: str,
    socket: socket.socket,
    lock: Union[threading.Lock, None],
    response: str,
    attempts: int = SOCKET_TX_ATTEMPTS,
    timeout: int = 5,
    size: int = 1024 * 8,
    delay_s: Union[None, float] = None
    ) -> Tuple[bool, str]: Send a message over a socket and wait for a response.

"""
import json
import socket
import threading
import time
import typing

from aqueduct.core.socket_constants import SOCKET_DELAY_S
from aqueduct.core.socket_constants import SOCKET_TX_ATTEMPTS


def string_to_bool(string: str) -> bool:
    """
    Convert a string to a boolean.

    :param string: The string to convert.
    :return: The boolean value.
    """
    if str(string).lower() in ("true", "1"):
        return True
    elif str(string).lower() in ("false", "0"):
        return False
    else:
        raise TypeError(f"Could not convert {string} to a boolean value.")


def split_packets(message: bytes) -> typing.Tuple[bytes]:
    """
    Split a byte string message into packets and extract the command and payload pairs.

    :param message: The byte string message to be split.
    :type message: bytes
    :return: A tuple of tuples containing the command and payload pairs.
    :rtype: tuple
    """
    if b"][" in message:
        packets = message.split(b"][")

        for i in range(len(packets)):
            if i == 0:
                packets[i] = packets[i] + b"]"
            elif i == len(packets) - 1:
                packets[i] = b"[" + packets[i]
    else:
        packets = (message,)

    return tuple(packets)


# pylint: disable=too-many-arguments
def send_and_wait_for_rx(
    message: str,
    sock: socket.socket,
    lock: typing.Union["threading.Lock", None],
    response: str,
    attempts: int = SOCKET_TX_ATTEMPTS,
    timeout: int = 5,
    size: int = 1024 * 8,
    delay_s: typing.Union[None, float] = None,
) -> typing.Tuple[bool, str]:
    """
    Send a message over a socket and wait for a response.

    Args:
        message: The message to send.
        sock: The socket to use for sending and receiving.
        lock: The lock to use for synchronizing socket access.
        response: The expected response to the message.
        attempts: The number of attempts to make.
        timeout: The timeout value for the socket.
        size: The size of the buffer for receiving data.
        delay_s: The delay between message sends.

    Returns:
        A tuple containing a boolean indicating success and the response data.
    """
    i = 0
    while i < attempts:
        try:
            if lock:
                with lock:
                    sock.settimeout(timeout)
                    sock.send(message)
                    time.sleep(SOCKET_DELAY_S)
                    data = sock.recv(size)
            else:
                sock.settimeout(timeout)
                sock.send(message)
                time.sleep(SOCKET_DELAY_S)
                data = sock.recv(size)

        except socket.timeout:
            # Socket timeout occurred, increment attempt counter and continue the loop.
            i += 1
            continue

        try:
            packets = split_packets(data)
            for packet in packets:
                j = json.loads(packet)
                if j[0] == response:
                    if delay_s is not None:
                        time.sleep(delay_s)
                    return True, j[1]
        except (json.decoder.JSONDecodeError, IndexError):
            # Error occurred while parsing the received data as JSON, continue the loop.
            continue

        i += 1

    # No successful response within the given attempts, return False and None.
    if delay_s is not None:
        time.sleep(delay_s)
    return False, None
