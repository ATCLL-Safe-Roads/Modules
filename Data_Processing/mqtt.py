import json
import paho.mqtt.client as mqtt
import os

from json import JSONDecodeError
from threading import Thread

from dotenv import load_dotenv

load_dotenv()

ATCLL_BROKER_HOST = os.getenv('ATCLL_BROKER_HOST')
ATCLL_BROKER_PORT = int(os.getenv('ATCLL_BROKER_PORT'))


class Consumer(Thread):
    def __init__(self, process_service):
        super().__init__()
        self.process_service = process_service

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(ATCLL_BROKER_HOST, ATCLL_BROKER_PORT)

    def on_connect(self, client, userdata, flags, rc):
        for p_id in self.process_service.p_ids:
            self.client.subscribe(f'p{p_id}/jetson/camera/count')
            self.client.subscribe(f'p{p_id}/jetson/radar/traffic/1')
            self.client.subscribe(f'p{p_id}/jetson/radar/traffic/2')
            self.client.subscribe(f'p{p_id}/jetson/radar')

    def on_message(self, client, userdata, message):
        try:
            msg = json.loads(message.payload.decode('utf-8'))
            msg_topic = message.topic
        except JSONDecodeError:
            print(f'ERROR: Unable to decode message {message.payload.decode("utf-8")}')
            return

        if not msg:
            return

        if msg_topic.endswith('jetson/camera/count'):
            p_id = int(msg_topic.split('/')[0][1:])

            self.process_service.camera_count(msg, p_id)
            self.process_service.check_for_traffic(p_id)

        elif msg_topic.endswith('jetson/radar/traffic/1') or msg_topic.endswith('jetson/radar/traffic/2'):
            p_id = int(msg_topic.split('/')[0][1:])
            heading = int(msg_topic.split('/')[-1])

            self.process_service.radar_traffic(msg, p_id, heading)
            self.process_service.check_for_traffic(p_id, heading)

        elif msg_topic.endswith('jetson/radar'):
            p_id = int(msg_topic.split('/')[0][1:])

            self.process_service.check_wrong_way(msg, p_id)

    def run(self):
        self.client.loop_forever()


class Producer:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(ATCLL_BROKER_HOST, ATCLL_BROKER_PORT)

    def publish(self, message, topic):
        result = self.client.publish(topic, message, retain=True, qos=0)
        status = result[0]
        return status
