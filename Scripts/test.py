import json
import paho.mqtt.client as mqtt

ATCLL_BROKER_HOST="atcll-data.nap.av.it.pt"
ATCLL_BROKER_PORT=1884

class Producer:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(ATCLL_BROKER_HOST, ATCLL_BROKER_PORT)

    def publish(self, message, topic):
        result = self.client.publish(topic, message, retain=True, qos=0)
        status = result[0]
        return status

data = None
with open('events.json', encoding='utf-8') as f:
    data = json.load(f)

Producer = Producer()

for event in data["events"]:
   
    status = Producer.publish(json.dumps(event, ensure_ascii=False, default=str).encode('utf-8'), "/events")

    if status != 0:
        print("Error publishing message")
    else:
        print("Message published")