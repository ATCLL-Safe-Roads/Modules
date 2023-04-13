from fastapi_mqtt import FastMQTT, MQTTConfig

from app.database import Event, Flow
from datetime import datetime
import json

HOST = 'atcll-data.nap.av.it.pt'
PORT = 1884

mqtt_config = MQTTConfig(host=HOST, port=PORT)

mqtt = FastMQTT(config=mqtt_config)

@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("/events")
    mqtt.client.subscribe("/traffic-flow-here")
    print("Connected: ", client, flags, rc, properties)

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    if topic == "/events":
        if properties["retain"] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        s = datetime.strptime(j["start"], '%Y-%m-%dT%H:%M:%S%z')
        j["start"] = s
        e = datetime.strptime(j["end"], '%Y-%m-%dT%H:%M:%S%z')
        j["end"] = e
        Event.insert_one(j)
    if topic == "/traffic-flow-here":
        if properties["retain"] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        t = datetime.strptime(j["timestamp"], '%Y-%m-%dT%H:%M:%S%z')
        j["timestamp"] = t
        Flow.insert_one(j)
    print("Received message: ", topic, payload.decode(), qos, properties)
