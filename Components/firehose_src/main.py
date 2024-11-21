import sys
import json
import time
import logging
import boto3
import backoff
import threading
from awsgreengrasspubsubsdk.pubsub_client import AwsGreengrassPubSubSdkClient
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter
class Config:
    def __init__(self):
        self.delivery_stream_name = "lab4-firehose-stream-put"
        self.region = "us-east-2"

class FirehoseClient:
    """
    AWS Firehose client to send records and monitor metrics.

    Attributes:
        config (object): Configuration object with delivery stream name and region.
        delivery_stream_name (str): Name of the Firehose delivery stream.
        firehose (boto3.client): Boto3 Firehose client.
    """

    def __init__(self, config):
        """
        Initialize the FirehoseClient.

        Args:
            config (object): Configuration object with delivery stream name and region.
        """
        self.config = config
        self.delivery_stream_name = config.delivery_stream_name
        self.region = config.region
        self.firehose = boto3.client("firehose", region_name=self.region)
        self.total_records_sent = 0


    @backoff.on_exception(
        backoff.expo, Exception, max_tries=5, jitter=backoff.full_jitter
    )
    def put_record_batch(self, data: list, batch_size: int = 500):
        """
        Put records in batches to Firehose with backoff and retry.

        Args:
            data (list): List of data records to be sent to Firehose.
            batch_size (int): Number of records to send in each batch. Default is 500.

        This method attempts to send records in batches to the Firehose delivery stream.
        It retries with exponential backoff in case of exceptions.
        """
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]

            # print records print for debugging
            self.total_records_sent += len(batch)
            logger.info(f"Sending batch of {len(batch)} records to Firehose. Total batches sent: {self.total_records_sent}")
            
            record_dicts = [{"Data": json.dumps(record)} for record in batch]
            try:
                response = self.firehose.put_record_batch(
                    DeliveryStreamName=self.delivery_stream_name, Records=record_dicts
                )
            except Exception as e:
                logger.info(f"Failed to send batch of {len(batch)} records. Error: {e}")



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
class MyAwsGreengrassV2Component():
    def __init__(self):
        self.lock = threading.Lock()  # Lock to prevent
        # initialize client
        base_topic = "GGHW" # only used if no topic is provided to client.publish_message. We don't use it in this simple example
        self.client = AwsGreengrassPubSubSdkClient(base_topic=base_topic, default_message_handler=self.message_handler)
        self.client.activate_mqtt_pubsub()
        self.client.activate_ipc_pubsub()

        config = Config()
        self.firehose_client = FirehoseClient(config)  # Initialize Firehose client
        self.current_list = 1
        self.firehose_data_list_1 = []  # Initialize data list to store records
        self.firehose_data_list_2 = []  # Initialize data list to store records
        self.firehose_last_send_time = time.time()
        self.firehose_send_interval = 10  # Send data to Firehose every 10 seconds at most

        # message formatter for consistent messaging API (starting point for routes etc)
        self.message_formatter = PubSubMessageFormatter()

        # Expose the client methods as class methods
        self.subscribe_to_topic  = self.client.subscribe_to_topic

    def publish_message(self, message, topic=None):
        sdk_message = self.message_formatter.get_message(message=message)
        self.client.publish_message('ipc_mqtt', sdk_message, topic=topic)  # Publish using MQTT and IPC protocol
        return sdk_message

    def message_handler(self, protocol, topic, message_id, status, route, message_payload):
        # lets make sure two threads arent accessing firehose_data_list at the same time by using a lock
        with self.lock:
            if self.current_list == 1:
                self.firehose_data_list_1.append(message_payload)
            else:
                self.firehose_data_list_2.append(message_payload)  

if __name__ == "__main__":
    # define topics
    subscribe_topic = "cloud/clients/+/data"

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
    firehose_send_interval = 2  # Send data to Firehose every 10 seconds at most
    try:
        while True:
            # send to firehose at specified time intervaltime interval
            # and flip the list that gets appended to on message receipt
            time.sleep(firehose_send_interval)
            with client.lock:
                list_to_send = client.current_list
                if list_to_send == 1:
                    client.current_list = 2
                else:
                    client.current_list = 1

            # actuallhy send the data and reset list
            if list_to_send == 1:
                client.firehose_client.put_record_batch(client.firehose_data_list_1)
                client.firehose_data_list_1 = []
            else:
                client.firehose_client.put_record_batch(client.firehose_data_list_2)
                client.firehose_data_list_2 = []
            
    except Exception as e:
        logger.error(f"Error running the component: {e}")
