from fastapi_mqtt import FastMQTT, MQTTConfig

HOST = 'atcll-data.nap.av.it.pt'
PORT = 1884

mqtt_config = MQTTConfig(host=HOST, port=PORT)

mqtt = FastMQTT(config=mqtt_config)

@mqtt.on_connect()
def connect(client, flags, rc, properties):
    mqtt.client.subscribe("/events")
    print("Connected: ", client, flags, rc, properties)

@mqtt.on_message()
async def message(client, topic, payload, qos, properties):
    print("Received message: ", topic, payload.decode(), qos, properties)
