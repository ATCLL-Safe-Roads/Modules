import json
import paho.mqtt.client as mqtt

class Consumer:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("mosquitto")
        print(self)

    def run(self):
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("subscribe")
        self.client.subscribe("self.topic") # TODO : Add the topic

    def on_message(self, client, userdata, msg):
        try:
            message = json.loads(msg.payload.decode("utf-8"))
            #serializer = AlertSerializer(data=message)
            #if serializer.is_valid():
            #    serializer.save()
            #    print(msg.topic + ' ' + message.__str__())
        except json.decoder.JSONDecodeError:
            print("Alert in invalid format")