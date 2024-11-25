import os
from typing import Callable, Any, Optional

from PyP100.PyP100 import Device
from PyP100.PyP110 import P110

from power_monitoring_plug import PowerMonitoringPlug


def execute_device_method(device: Device, function: Callable[[Device], Any]) -> Any:
    try:
        return function(device)
    except:
        # Force protocol to be None to re-authenticate. The library does not support this directly, and it can cause
        # issues when the script is running for a long time.
        device.protocol = None

        device.handshake()
        device.login()

    return function(device)


class P110PowerMonitoringPlug(PowerMonitoringPlug):

    def __init__(self, p110_address: str, tp_link_email: Optional[str] = None, tp_link_password: Optional[str] = None):
        if tp_link_email is None:
            tp_link_email = os.getenv('TP_LINK_EMAIL')
            if tp_link_email is None:
                raise Exception('TP_LINK_EMAIL environment variable must be set.')

        if tp_link_password is None:
            tp_link_password = os.getenv('TP_LINK_PASSWORD')
            if tp_link_password is None:
                raise Exception('TP_LINK_PASSWORD environment variable must be set.')

        self.__p110 = P110(p110_address, tp_link_email, tp_link_password)

    def get_power(self) -> float:
        energy_usage = execute_device_method(self.__p110, lambda d: d.getEnergyUsage())
        return energy_usage['current_power'] / 1000

    def get_status(self) -> bool:
        return execute_device_method(self.__p110, lambda d: d.get_status())

    def set_status(self, status: bool) -> None:
        execute_device_method(self.__p110, lambda d: d.set_status(status))
