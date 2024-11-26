import os
import time
import traceback
from typing import Callable, Optional

import paho.mqtt.client as mqtt

from power_monitoring_plug import PowerMonitoringPlug


class MqttClient:

    def __init__(self, host: str, port: int):
        self.__subscriptions: dict[str, list[Callable[[str, str], None]]] = {}

        self.__client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        self.__client.on_connect = self.__on_connect
        self.__client.on_message = self.__on_message

        self.__client.connect(host, port, 60)
        self.__client.loop_start()

    def subscribe(self, topic: str, callback: Callable[[str, str], None]):
        if topic not in self.__subscriptions:
            self.__subscriptions[topic] = []

        self.__subscriptions[topic].append(callback)
        self.__client.subscribe(topic)

    def publish(self, topic: str, value: str, qos: int, retain: bool):
        self.__client.publish(topic, value, qos, retain)

    def __on_connect(self, client, userdata, flags, reason_code, properties):
        for topic in self.__subscriptions.keys():
            self.__client.subscribe(topic)

    def __on_message(self, client, userdata, msg):
        topic = msg.topic
        if topic not in self.__subscriptions:
            return

        value = msg.payload.decode('utf-8')
        callbacks = self.__subscriptions[topic]
        for callback in callbacks:
            try:
                callback(topic, value)
            except:
                print('An exception got caught during a MQTT subscription callback. See stacktrace below.')
                print(traceback.format_exc())


global_mqtt_client: Optional[MqttClient] = None
if os.getenv('MQTT_BROKER_ADDRESS') is not None:
    print('MQTT_BROKER_ADDRESS environment variable defined, connecting to MQTT broker!')
    global_mqtt_client = MqttClient(
        host=os.getenv('MQTT_BROKER_ADDRESS'),
        port=int(os.getenv('MQTT_BROKER_PORT', '1883')),
    )
else:
    print('No MQTT_BROKER_ADDRESS environment variable defined, \'mqtt\' type plugs won\'t work.')


class MqttPowerMonitoringPlug(PowerMonitoringPlug):

    def __init__(self, topic_prefix: str,
                 status_topic: str = '{topic_prefix}/status',
                 power_topic: str = '{topic_prefix}/power',
                 mqtt_client: Optional[MqttClient] = None):
        if mqtt_client is None:
            mqtt_client = global_mqtt_client
        if mqtt_client is None:
            raise Exception('No MQTT client provided.')

        self.__status_topic = status_topic.format(topic_prefix=topic_prefix)
        self.__power_topic = power_topic.format(topic_prefix=topic_prefix)

        self.__status: Optional[bool] = None
        self.__power: Optional[float] = None

        mqtt_client.subscribe(self.__status_topic, self.__mqtt_status_callback)
        mqtt_client.subscribe(self.__power_topic, self.__mqtt_power_callback)

    def __mqtt_status_callback(self, topic: str, value: str):
        self.__status = value == '1'

    def __mqtt_power_callback(self, topic: str, value: str):
        self.__power = float(value)

    def wait_until_ready(self):
        while self.__status is None or self.__power is None:
            time.sleep(0.01)

    def get_power(self) -> float:
        if self.__power is None:
            raise Exception('Did not receive power data yet.')

        return self.__power

    def get_status(self) -> bool:
        if self.__status is None:
            raise Exception('Did not receive status data yet.')

        return self.__status

    def set_status(self, status: bool) -> None:
        global_mqtt_client.publish(self.__status_topic, '1' if status else '0', qos=2, retain=True)
