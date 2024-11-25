import datetime
import os
from typing import Optional, TypedDict, NotRequired

from discord_webhook import DiscordWebhook

from p110_power_monitoring_plug import P110PowerMonitoringPlug
from power_monitoring_plug import PowerMonitoringPlug


class TapoPowerSavePlug:

    def __init__(self, name: str, plug: PowerMonitoringPlug, power_threshold: float, max_low_power_time: float, discord_log: bool):
        self.__name = name
        self.__plug = plug
        self.__power_threshold = power_threshold
        self.__max_low_power_time = max_low_power_time
        self.__discord_log = discord_log

        self.__low_power_since: Optional[datetime.datetime] = None

    def update(self):
        is_on = self.__plug.get_status()
        if not is_on:
            return

        power = self.__plug.get_power()
        if power < self.__power_threshold:
            if self.__low_power_since is None:
                self.__low_power_since = datetime.datetime.now()
            elif datetime.datetime.now() - self.__low_power_since > datetime.timedelta(seconds=self.__max_low_power_time):
                self.__plug.set_status(False)

                print(f'Plug {self.__name} has been turned off.')

                if self.__discord_log:
                    self.__log_turned_off()
        else:
            self.__low_power_since = None

    def __log_turned_off(self):
        discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
        if discord_webhook_url is not None:
            message = f':electric_plug: The tapo plug `{self.__name}` has been turned off because it had a low power usage for more than {self.__max_low_power_time} seconds.'
            DiscordWebhook(url=discord_webhook_url, content=message).execute()
        else:
            print('The environment variable DISCORD_WEBHOOK_URL should be set in order for discord logs to work.')


class TapoPowerSavePlugConfig(TypedDict):
    type: NotRequired[str]  # 'p110' (default)
    address: NotRequired[str]  # Used when type is 'p110'
    power_threshold: float
    max_low_power_time: float
    discord_log: NotRequired[bool]


def build_tapo_power_save_plug(name: str, config: TapoPowerSavePlugConfig) -> TapoPowerSavePlug:
    plug_type = config.get('type', 'p110')
    if plug_type == 'p110':
        plug = P110PowerMonitoringPlug(config.get('address'))
    else:
        raise Exception(f'Invalid plug type \'{plug_type}\'')

    return TapoPowerSavePlug(
        name,
        plug,
        config.get('power_threshold'),
        config.get('max_low_power_time'),
        config.get('discord_log', False)
    )
