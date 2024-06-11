import os
import time

import yaml
from dotenv import load_dotenv

from tapo_power_save_plug import TapoPowerSavePlug, build_tapo_power_save_plug


load_dotenv()


def load_power_save_plugs(file_name: str) -> list[TapoPowerSavePlug]:
    with open(file_name) as stream:
        config = yaml.safe_load(stream)

    plugs = []
    for name, plug_config in config['power-save-plugs'].items():
        plug_config = {k.replace('-', '_'): v for k, v in plug_config.items()}
        plug = build_tapo_power_save_plug(name, plug_config)
        plugs.append(plug)

    return plugs


def main():
    config_file = os.getenv('CONFIG_FILE', 'config.yml')
    update_interval = float(os.getenv('UPDATE_INTERVAL', '30'))

    print(f'CONFIG_FILE={config_file}')
    print(f'UPDATE_INTERVAL={update_interval}')

    plugs = load_power_save_plugs(config_file)
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
