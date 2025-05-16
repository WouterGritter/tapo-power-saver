import datetime
from typing import Optional, TypedDict

from discord_utils import log_discord_message
from intelligent_plug import IntelligentPlug
from power_monitoring_plug import PowerMonitoringPlug
from power_monitoring_plug_factory import PowerMonitoringPlugConfig, build_power_monitoring_plug


class PowerSavingPlug(IntelligentPlug):

    def __init__(self, name: str, backend: PowerMonitoringPlug, power_threshold: float, max_low_power_time: float):
        self.__name = name
        self.__backend = backend
        self.__power_threshold = power_threshold
        self.__max_low_power_time = max_low_power_time

        self.__low_power_since: Optional[datetime.datetime] = None
        self.__was_on: Optional[bool] = None

    def get_backend(self) -> PowerMonitoringPlug:
        return self.__backend

    def update(self):
        is_on = self.__backend.get_status()

        if is_on and self.__was_on is False:
            # Tapo plug just got turned on externally.
            self.__log_turned_on()

        self.__was_on = is_on

        if not is_on:
            self.__low_power_since = None
            return

        power = self.__backend.get_power()
        if power < self.__power_threshold:
            if self.__low_power_since is None:
                self.__low_power_since = datetime.datetime.now()
            elif datetime.datetime.now() - self.__low_power_since > datetime.timedelta(seconds=self.__max_low_power_time):
                self.__backend.set_status(False)

                self.__log_turned_off()
        else:
            self.__low_power_since = None

    def __log_turned_off(self):
        message = f':electric_plug: The tapo plug `{self.__name}` has been turned off because it had a low power usage for more than {self.__max_low_power_time} seconds.'
        log_discord_message(message)

    def __log_turned_on(self):
        message = f':electric_plug: The tapo plug `{self.__name}` just got turned on externally :zap:! It will turn off automatically after it has a low power usage for more than {self.__max_low_power_time} seconds.'
        log_discord_message(message)


class PowerSavingPlugConfig(TypedDict, PowerMonitoringPlugConfig):
    power_threshold: float
    max_low_power_time: float


def build_power_saving_plug(name: str, config: PowerSavingPlugConfig) -> PowerSavingPlug:
    return PowerSavingPlug(
        name,
        build_power_monitoring_plug(config),
        config.get('power_threshold'),
        config.get('max_low_power_time'),
    )
