import datetime
import os
from typing import Optional, TypedDict, NotRequired

from PyP100.PyP110 import P110
from discord_webhook import DiscordWebhook


class TapoPowerSavePlug:
    def __init__(self, name: str, p110: P110, power_threshold: float, max_low_power_time: float, discord_log: bool):
        self.__name = name
        self.__p110 = p110
        self.__power_threshold = power_threshold
        self.__max_low_power_time = max_low_power_time
        self.__discord_log = discord_log

        self.__low_power_since: Optional[datetime.datetime] = None

    def update(self):
        is_on = self.__fetch_status()
        if not is_on:
            return

        power = self.__fetch_current_power()
        if power < self.__power_threshold:
            if self.__low_power_since is None:
                self.__low_power_since = datetime.datetime.now()
            elif datetime.datetime.now() - self.__low_power_since > datetime.timedelta(seconds=self.__max_low_power_time):
                self.__set_status(False)
        else:
            self.__low_power_since = None

    def __set_status(self, status: bool):
        self.__p110.set_status(status)

        if status is False and self.__discord_log:
            discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
            if discord_webhook_url is not None:
                message = f':electric_plug: The tapo plug `{self.__name}` has been turned off because it had a low power usage for more than {self.__max_low_power_time} seconds.'
                DiscordWebhook(url=discord_webhook_url, content=message).execute()
            else:
                print('The environment variable DISCORD_WEBHOOK_URL should be set in order for discord logs to work.')

    def __fetch_status(self) -> bool:
        return self.__p110.get_status()

    def __fetch_current_power(self) -> float:
        return self.__p110.getEnergyUsage()['current_power'] / 1000


class TapoPowerSavePlugConfig(TypedDict):
    address: str
    power_threshold: float
    max_low_power_time: float
    discord_log: NotRequired[bool]


def build_tapo_power_save_plug(name: str, config: TapoPowerSavePlugConfig) -> TapoPowerSavePlug:
    tp_link_email = os.getenv('TP_LINK_EMAIL')
    tp_link_password = os.getenv('TP_LINK_PASSWORD')

    if tp_link_email is None or tp_link_password is None:
        raise Exception('TP_LINK_EMAIL and TP_LINK_PASSWORD must be set as environment variables.')

    p110 = P110(config['address'], tp_link_email, tp_link_password)

    return TapoPowerSavePlug(
        name,
        p110,
        config.get('power_threshold'),
        config.get('max_low_power_time'),
        config.get('discord_log', False)
    )
