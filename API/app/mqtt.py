import json

from datetime import datetime
from fastapi_mqtt import FastMQTT, MQTTConfig

from app.database import Event, Flow
from app.config import settings
from app.schemas import FlowSchema, EventSchema

mqtt_config = MQTTConfig(host=settings.ATCLL_BROKER_HOST, port=settings.ATCLL_BROKER_PORT)
mqtt = FastMQTT(config=mqtt_config)


@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe('/events')
    mqtt.client.subscribe('/flows')
    print('INFO: Connected to MQTT Broker.')


@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    if topic == '/events':
        if properties['retain'] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        s = datetime.strptime(j['start'], '%Y-%m-%dT%H:%M:%S%z')
        j['start'] = s
        e = datetime.strptime(j['end'], '%Y-%m-%dT%H:%M:%S%z')
        j['end'] = e
        t = datetime.strptime(j['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
        j['timestamp'] = t
        # Replace if sourceid matches
        if Event.count_documents({'source': 'here', 'sourceid': j['sourceid']}):
            Event.replace_one({'source': 'here', 'sourceid': j['sourceid']}, j)
        # Insert only if it doesn't exist
        elif not Event.count_documents(dict(EventSchema(**j))):
            Event.insert_one(j)
    if topic == '/flows':
        if properties['retain'] == 1:
            return
        r = payload.decode()
        j = json.loads(r)
        t = datetime.strptime(j['timestamp'], '%Y-%m-%dT%H:%M:%S%z')
        j['timestamp'] = t
        # Insert only if it doesn't exist
        if not Flow.count_documents(dict(FlowSchema(**j))):
            Flow.insert_one(j)
    print(f'INFO: Received message on topic {topic} {payload.decode()[:100]}.')
