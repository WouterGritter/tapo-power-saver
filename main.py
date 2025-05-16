from dotenv import load_dotenv

from intelligent_plug import IntelligentPlug
from mqtt_power_monitoring_plug import MqttPowerMonitoringPlug
from power_notifying_plug import build_power_notifying_plug

load_dotenv()

import os
import time

import yaml

from power_saving_plug import build_power_saving_plug


def load_intelligent_plugs(file_name: str) -> list[IntelligentPlug]:
    with open(file_name) as stream:
        config = yaml.safe_load(stream)

    plugs: list[IntelligentPlug] = []

    for name, plug_config in (config.get('power-save-plugs') or {}).items():
        plug_config = {k.replace('-', '_'): v for k, v in plug_config.items()}
        plug = build_power_saving_plug(name, plug_config)
        plugs.append(plug)

    for name, plug_config in (config.get('power-notify-plugs') or {}).items():
        plug_config = {k.replace('-', '_'): v for k, v in plug_config.items()}
        plug = build_power_notifying_plug(name, plug_config)
        plugs.append(plug)

    print('Waiting until MQTT plugs are ready (if there are any)...')
    for plug in plugs:
        backend = plug.get_backend()
        if isinstance(backend, MqttPowerMonitoringPlug):
            backend.wait_until_ready()
    print('Done.')

    return plugs


def main():
    config_file = os.getenv('CONFIG_FILE', 'config.yml')
    update_interval = float(os.getenv('UPDATE_INTERVAL', '30'))

    print(f'CONFIG_FILE={config_file}')
    print(f'UPDATE_INTERVAL={update_interval}')

    plugs = load_intelligent_plugs(config_file)
    print(f'Loaded {len(plugs)} plug(s).')

    while True:
        for plug in plugs:
            try:
                plug.update()
            except Exception as ex:
                print(f'An exception occurred while attempting to update plug: {ex}')
        time.sleep(update_interval)


if __name__ == '__main__':
    main()
