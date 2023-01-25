"""
The aqueduct.core.socket_helpers module provides various helper functions for working with sockets.

Functions:
- string_to_bool(string: str) -> bool: Convert a string to a boolean value.
- send_and_wait_for_rx(message: str, socket: socket.socket, lock: Union[threading.Lock, None], response: str, attempts: int = SOCKET_TX_ATTEMPTS, timeout: int = 5, size: int = 1024 * 8, delay_s: Union[None, float] = None) -> Tuple[bool, str]: Send a message over a socket and wait for a response.

"""

import json
import threading
import time
import typing

from aqueduct.core.socket_constants import SOCKET_DELAY_S, SOCKET_TX_ATTEMPTS


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
        raise TypeError(
            "Could not convert {} to a boolean value.".format(string))


def send_and_wait_for_rx(
    message: str,
    socket: "socket.socket",
    lock: typing.Union["threading.Lock", None],
    response: str,
    attempts: int = SOCKET_TX_ATTEMPTS,
    timeout: int = 5,
    size: int = 1024 * 8,
    delay_s: typing.Union[None, float] = None,
) -> typing.Tuple[bool, str]:
    """
    Send a message over a socket and wait for a response.

    :param message: The message to send.
    :param socket: The socket to use for sending and receiving.
    :param lock: The lock to use for synchronizing socket access.
    :param response: The expected response to the message.
    :param attempts: The number of attempts to make.
    :param timeout: The timeout value for the socket.
    :param size: The size of the buffer for receiving data.
    :param delay_s: The delay between message sends.
    :return: A tuple containing a boolean indicating success and the response data.
    """
    i = 0
    while i < attempts:
        if lock:
            with lock:
                socket.settimeout(timeout)
                socket.send(message)
                time.sleep(SOCKET_DELAY_S)
                data = socket.recv(size)
        else:
            socket.settimeout(timeout)
            socket.send(message)
            time.sleep(SOCKET_DELAY_S)
            data = socket.recv(size)
        try:
            j = json.loads(data)
            if j[0] == response:
                if delay_s is not None:
                    time.sleep(delay_s)
                return True, j[1]
        except json.decoder.JSONDecodeError:
            continue
        i += 1
    if delay_s is not None:
        time.sleep(delay_s)
    return False, None
