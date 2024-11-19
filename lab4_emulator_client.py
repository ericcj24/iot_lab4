# Import SDK packages
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from awsgreengrasspubsubsdk.message_formatter import PubSubMessageFormatter
import time
import json
import pandas as pd
import numpy as np
import configparser
import os
import uuid

config = configparser.ConfigParser()
config.read('./config/config.ini')
DISCOVERY_HOST = config.get('Discovery Endpoint', 'name')
DISCOVERY__PORT = int(config.get('Discovery Endpoint', 'port'))
CORE_HOST = config.get('Core Endpoint', 'name')
CORE_PORT = int(config.get('Core Endpoint', 'port'))
GROUP_CA_PATH = "./groupCA/"
#TODO 1: modify the following parameters
#Starting and end index, modify this
num_devices = 1
device_name_formatter = 'picar_{}'

#Path to the dataset, modify this
data_path = "./vehicles/vehicle_{}.csv"
ca_path = "./keys/AmazonRootCA1.pem"
#Path to your certificates, modify this
certificate_formatter = "./certs/{}cert.pem"
key_formatter = "./keys/{}private.key"


class MQTTClient:
    def __init__(self, device_id, groupCA, cert, key, host, port):
        # For certificate based connection
        self.device_id = str(device_id)
        self.state = 0
        self.max_emission = -1
        self.client = AWSIoTMQTTClient(self.device_id)
        #TODO 2: modify your broker address
        self.client.configureEndpoint(host, port)
        self.client.configureCredentials(groupCA, key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage
        self.client.subscribeAsync(f"local/{device_id}/max_emission", 0, ackCallback=self.customSubackCallback, messageCallback=self.maxEmissionSubCallback)
        

    def customOnMessage(self, message):
        #TODO 3: fill in the function to show your received message
        print("client {} received payload {} from topic {}".format(self.device_id, message.payload, message.topic))

    def maxEmissionSubCallback(self, client, userdata, message):
        print(client)
        pass

    # Suback callback
    def customSubackCallback(self,mid, data):
        #You don't need to write anything here
        pass

    # Puback callback
    def customPubackCallback(self,mid):
        #You don't need to write anything here
        pass

    def publish(self, topic="local/picar_0/data"):
    # Load the vehicle's emission data
        df = pd.read_csv(data_path.format(self.device_id))
        for index, row in df.iterrows():
            # Create Payload for Greengrass Device
            payload = json.dumps(row.to_dict())
            
            # Publish the payload to the specified topic
            print(f"Publishing: {payload} to {topic}")
            self.client.publishAsync(topic, payload, 1, ackCallback=self.customPubackCallback)
            
            # Sleep to simulate real-time data publishing
            
class discoveryHandler():
    def __init__(self) -> None:
        self.discoveryInfoProvider = DiscoveryInfoProvider()
        self.discoveryInfoProvider.configureEndpoint(DISCOVERY_HOST, port=DISCOVERY__PORT)
        self.discoveryInfoProvider.configureTimeout(10)
    
    def discoverThing(self, caPath, deviceCert, deviceKey, thingName):
        try:
            self.discoveryInfoProvider.configureCredentials(caPath, deviceCert, deviceKey)
            discoveryInfo = self.discoveryInfoProvider.discover(thingName)
            caList = discoveryInfo.getAllCas()
            coreList = discoveryInfo.getAllCores()
            groupId, ca = caList[0]
            coreInfo = coreList[0]
            print("Discovered GGC: %s from Group: %s" % (coreInfo.coreThingArn, groupId))

            print("Now we persist the connectivity/identity information...")
            groupCA = GROUP_CA_PATH + groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
            if not os.path.exists(GROUP_CA_PATH):
                os.makedirs(GROUP_CA_PATH)
            groupCAFile = open(groupCA, "w")
            groupCAFile.write(ca)
            groupCAFile.close()
            for connectivityInfo in coreInfo.connectivityInfoList:
                currentHost = connectivityInfo.host
                currentPort = connectivityInfo.port

            print("Now proceed to the connecting flow...")
            return groupCA, currentHost, currentPort
        except DiscoveryInvalidRequestException as e:
            print("Invalid discovery request detected!")
            print("Type: %s" % str(type(e)))
            print("Error message: %s" % str(e))
            print("Stopping...")
        except BaseException as e:
            print("Error in discovery!")
            print("Type: %s" % str(type(e)))
            print("Error message: %s" % str(e))



print("Loading vehicle data...")
data = []
for i in range(num_devices):
    device_id = device_name_formatter.format(i)
    a = pd.read_csv(data_path.format(device_id))
    data.append(a)

print("Initializing MQTTClients...")
clients = []
for i in range(num_devices):
    device_id = device_name_formatter.format(i)
    print("device id:", device_id)
    certificate = certificate_formatter.format(device_id,device_id)
    key = key_formatter.format(device_id,device_id)
    discoveryObjectHandler = discoveryHandler()
    groupCA, host, port = discoveryObjectHandler.discoverThing(ca_path, certificate, key, device_id)
    client = MQTTClient(device_id, groupCA, certificate, key, host, port)
    client.client.connect()
    clients.append(client)
 
while True:
    print("send now?")
    x = input()
    if x == "s":
        for i,c in enumerate(clients):
            c.publish(f'local/{c.device_id}/data')

    elif x == "d":
        for c in clients:
            c.client.disconnect()
        print("All devices disconnected")
        exit()
    else:
        print("wrong key pressed")

    time.sleep(3)





