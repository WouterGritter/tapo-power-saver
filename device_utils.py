from typing import TypeVar, Callable

from PyP100.PyP100 import Device

T = TypeVar('T', bound=Device)
R = TypeVar('R')


def execute_device_method(device: T, function: Callable[[T], R]) -> R:
    try:
        return function(device)
    except:
        # Force protocol to be None to re-authenticate. The library does not support this directly, and it can cause
        # issues when the script is running for a long time.
        device.protocol = None

        device.handshake()
        device.login()

    return function(device)
