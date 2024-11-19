import sys
import json
import time
import logging
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print('Success')
class Car():
    def __init__(self, name: str) -> None:
        self.name = name
        self.max_emission = -1

    def update_max_emission(self, emission: float):
        if emission > self.max_emission:
            self.max_emission = emission
 
class MaxEmissionsComponent():
    def __init__(self, cars: int):
        # initialize client
        base_topic = "local/Thing" # only used if no topic is provided to client.publish_message. We don't use it in this simple example
        self.client = AwsGreengrassPubSubSdkClient(base_topic=base_topic, default_message_handler=self.message_handler)
        self.client.activate_mqtt_pubsub()
        self.client.activate_ipc_pubsub()
        self.devices = {}
        # message formatter for consistent messaging API (starting point for routes etc)
        self.message_formatter = PubSubMessageFormatter()

        # Expose the client methods as class methods
        self.subscribe_to_topic  = self.client.subscribe_to_topic
        for topic in self.get_init_subscribe_topics(cars):
            self.subscribe_to_topic('ipc_mqtt', topic)
    
    def publish_message(self, message, topic=None):
        sdk_message = self.message_formatter.get_message(message=message)
        self.client.publish_message('ipc_mqtt', sdk_message, topic=topic)  # Publish using MQTT and IPC protocol
        return sdk_message

    def message_handler(self, protocol, topic:str, message_id, status, route, message_payload: str):
        origin_device_name = topic.split('/')[1]
        emission_value = message_payload['vehicle_C02']
        self.devices.setdefault(origin_device_name, Car(origin_device_name))
        device = self.devices[origin_device_name]
        device.update_max_emission(emission_value)
        self.publish_message(f'Current Max Emission: {device.max_emission}', topic=f'local/{origin_device_name}/max_emission')
        self.publish_message(f'Vehicle Data: {message_payload}', topic=f'cloud/clients/{origin_device_name}/data')
        logger.info(f"Received message on {topic}: {message_payload}")

    def get_init_subscribe_topics(self, num_devices: int):
        subscribe_topics = [f'local/picar_{num}/data' for num in range(num_devices)]
        return subscribe_topics

if __name__ == "__main__":
    # define topics

    # Initialize client
    client = MaxEmissionsComponent(5)

    # subscribe to topic
    # NOTE since we are using the sdk here, the client requires messages json formatted
    # as show below, where the contents of "message" is the actual payload/custom data.
    # {
    # "sdk_version": "0.1.4",
    # "message_id": "20240930180857201116",
    # "status": 200,
    # "route": "default_message_handler",
    # "message": { "user_msg": "Hello World, from IoT CONSOLE" }
    # }
    try:
        while True:
            pass
    except Exception as e:
        logger.error(f"Error running the component: {e}")
