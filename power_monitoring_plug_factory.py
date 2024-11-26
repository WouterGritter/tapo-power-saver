from typing import TypedDict, NotRequired

from mqtt_power_monitoring_plug import MqttPowerMonitoringPlug
from p110_power_monitoring_plug import P110PowerMonitoringPlug
from power_monitoring_plug import PowerMonitoringPlug


class PowerMonitoringPlugConfig(TypedDict):
    type: NotRequired[str]  # 'p110' (default) or 'mqtt'
    address: NotRequired[str]  # Used when type is 'p110'
    topic: NotRequired[str]  # Used when type is 'mqtt'


def build_power_monitoring_plug(config: PowerMonitoringPlugConfig) -> PowerMonitoringPlug:
    plug_type = config.get('type', 'p110')
    if plug_type == 'p110':
        return P110PowerMonitoringPlug(config.get('address'))
    elif plug_type == 'mqtt':
        return MqttPowerMonitoringPlug(config.get('topic'))
    else:
        raise Exception(f'Invalid plug type \'{plug_type}\'')