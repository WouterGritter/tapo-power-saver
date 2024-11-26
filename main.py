from dotenv import load_dotenv

from mqtt_power_monitoring_plug import MqttPowerMonitoringPlug

load_dotenv()

import os
import time

import yaml

from power_saving_plug import PowerSavingPlug, build_power_saving_plug


def load_power_saving_plugs(file_name: str) -> list[PowerSavingPlug]:
    with open(file_name) as stream:
        config = yaml.safe_load(stream)

    plugs = []
    for name, plug_config in config['power-save-plugs'].items():
        plug_config = {k.replace('-', '_'): v for k, v in plug_config.items()}
        plug = build_power_saving_plug(name, plug_config)
        plugs.append(plug)

    print('Waiting until MQTT plugs are ready (if there are any)...')
    for plug in plugs:
        if isinstance(plug, MqttPowerMonitoringPlug):
            plug.wait_until_ready()
    print('Done.')

    return plugs


def main():
    config_file = os.getenv('CONFIG_FILE', 'config.yml')
    update_interval = float(os.getenv('UPDATE_INTERVAL', '30'))

    print(f'CONFIG_FILE={config_file}')
    print(f'UPDATE_INTERVAL={update_interval}')

    plugs = load_power_saving_plugs(config_file)
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
