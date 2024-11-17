import sys
import json
import time
import logging
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class MyAwsGreengrassV2Component():
    def __init__(self):
        # initialize client
        base_topic = "GGHW" # only used if no topic is provided to client.publish_message. We don't use it in this simple example
        self.client = AwsGreengrassPubSubSdkClient(base_topic=base_topic, default_message_handler=self.message_handler)
        self.client.activate_mqtt_pubsub()
        self.client.activate_ipc_pubsub()

        # message formatter for consistent messaging API (starting point for routes etc)
        self.message_formatter = PubSubMessageFormatter()

        # Expose the client methods as class methods
        self.subscribe_to_topic  = self.client.subscribe_to_topic

    def publish_message(self, message, topic=None):
        sdk_message = self.message_formatter.get_message(message=message)
        self.client.publish_message('ipc_mqtt', sdk_message, topic=topic)  # Publish using MQTT and IPC protocol
        return sdk_message
    def message_handler(self, protocol, topic, message_id, status, route, message_payload):
        logger.info(f"Received message on {topic}: {message_payload}")


if __name__ == "__main__":
    # define topics
    subscribe_topic = "GGHelloWorld/inbox"
    publish_topic = "GGHelloWorld/outbox"

    # Initialize client
    client = MyAwsGreengrassV2Component()

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
    client.subscribe_to_topic("ipc_mqtt", subscribe_topic)

    try:
        while True:
            message = {"user_msg": "Hello World, from GreenGrassCore V2"}
            sdk_message = client.publish_message( message, topic=publish_topic)  # Publish using MQTT and IPC protocol
            logger.info(f"Published sdk message to {publish_topic}: {sdk_message}")
            time.sleep(5)
    except Exception as e:
        logger.error(f"Error running the component: {e}")
