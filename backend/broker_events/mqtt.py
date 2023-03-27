import paho.mqtt.client as mqtt
import requests
import json

HOST = 'atcll-data.nap.av.it.pt'
PORT = 1884

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN


class Consumer(object):
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(HOST, PORT)

    def on_connect(self, client, userdata, flags, rc):
        print("Subscribing to /events")
        client.subscribe("/events")

    def on_message(self, client, userdata, msg):
        try:
            msg_decoded = json.loads(msg.payload.decode("utf-8"))
            print(msg.topic, msg_decoded)
        except:
            print("Error decoding message")

    def run(self):
        self.client.loop_forever()


class Producer(object):
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(HOST, PORT)

    def publish(self, message, topic="/events"):
        result = self.client.publish(topic, message, retain=True)
        status = result[0]
        return status
