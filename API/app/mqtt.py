import json

from datetime import datetime
from fastapi_mqtt import FastMQTT, MQTTConfig

from app.database import Event, Flow
from app.config import settings

mqtt_config = MQTTConfig(host=settings.ATCLL_BROKER_HOST, port=settings.ATCLL_BROKER_PORT)

mqtt = FastMQTT(config=mqtt_config)

ide = 0
idf = 0


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("/events")
    mqtt.client.subscribe("/traffic-flow-here")
    mqtt.client.subscribe("/flows")
    print("Connected: ", client, flags, rc, properties)


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    if topic == "/events":
        global ide
        if properties["retain"] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        s = datetime.strptime(j["start"], '%Y-%m-%dT%H:%M:%S%z')
        j["start"] = s
        e = datetime.strptime(j["end"], '%Y-%m-%dT%H:%M:%S%z')
        j["end"] = e
        j["id"] = ide
        ide += 1
        Event.insert_one(j)
    if topic == "/traffic-flow-here":
        global idf
        if properties["retain"] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        t = datetime.strptime(j["timestamp"], '%Y-%m-%dT%H:%M:%S%z')
        j["timestamp"] = t
        j["id"] = idf
        idf += 1
        Flow.insert_one(j)
    if topic == "/flows":
        if properties["retain"] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        t = datetime.strptime(j["timestamp"], "%Y-%m-%d %H:%M:%S.%f%z")
        j["timestamp"] = t
        j["id"] = idf
        idf += 1
        Flow.insert_one(j)
    print("Received message: ", topic, payload.decode(), qos, properties)
