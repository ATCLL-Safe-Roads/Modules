import paho.mqtt.client as mqtt
import requests
import json
import process

HOST = 'atcll-data.nap.av.it.pt'
PORT = 1884

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN


class Consumer(object):
    def __init__(self):
        # Variables
        self.post_ids = [1, 3, 4, 10, 11, 12, 14, 15, 18, 19, 21, 22, 23, 24, 25, 27, 28, 29, 30, 31, 32, 33, 35, 36,
                         38, 39, 41, 37, 40, 44]
        self.average_speeds = {id: 0 for id in self.post_ids}
        self.car_count = {id: 0 for id in self.post_ids}
        self.person_count = {id: 0 for id in self.post_ids}

        self.process = process.Processing()

        # Connect to MQTT broker
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(HOST, PORT)

    def on_connect(self, client, userdata, flags, rc):
        #print("Subscribing to /events")
        #client.subscribe("/events")
        for id in self.post_ids:
            self.client.subscribe(f"p{id}/jetson/radar/traffic/1")
            self.client.subscribe(f"p{id}/jetson/radar/traffic/2")
        pass

    def on_message(self, client, userdata, msg):
        try:
            msg_decoded = json.loads(msg.payload.decode("utf-8"))
            #print(msg.topic, msg_decoded)
            if msg.topic.endswith("jetson/camera/count"):
                postID = int(msg.topic.split("/")[0][1:])
                count = self.process.camera_count(msg.payload.decode("utf-8"), postID)
                self.person_count[postID] = count['person'] if 'person' in count.keys() else self.person_count[postID]
                flows = self.process.check_for_traffic(postID, self.average_speeds[postID], self.car_count[postID], self.person_count[postID])
                for flow in flows:
                    if flow:
                        Producer().publish(flow, topic="/flows")
            elif msg.topic.endswith("jetson/radar/traffic/1") or msg.topic.endswith("jetson/radar/traffic/2"):
                postID = int(msg.topic.split("/")[0][1:])
                heading = int(msg.topic.split("/")[-1])
                average_speed, cars_count = self.process.radar_traffic(msg.payload.decode("utf-8"), postID, heading)
                key = f"{postID}:{heading}"
                self.average_speeds[key] = average_speed
                self.car_count[key] = cars_count
                flows = self.process.check_for_traffic(postID, self.average_speeds[key], self.car_count[key], self.person_count[postID], heading)
                for flow in flows:
                    if flow:
                        print(flow)
                        Producer().publish(flow, topic="/flows")
        except:
            print("Error decoding message")

    def run(self):
        self.client.loop_forever()


class Producer(object):
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(HOST, PORT)

    def publish(self, message, topic="/flows"):
        result = self.client.publish(topic, message, retain=True, qos=0)
        status = result[0]
        return status
