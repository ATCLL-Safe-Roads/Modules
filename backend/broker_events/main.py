import mqtt
import json
import requests
from threading import Thread
import time

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN
INCIDENT_URL = 'https://data.traffic.hereapi.com/v7/incidents'


class Broker(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        mqtt.Consumer().run()


def fetch_ti_here():

    # Aveiro
    lat = 40.64427
    lon = -8.64554
    rad = 500  # meters

    params = {
        'apiKey': API_KEY,
        'locationReferencing': 'shape',
        'in': f'circle:{lat},{lon};r={rad}'
    }
    r = requests.get(url=INCIDENT_URL, params=params)
    return r.json()


if __name__ == "__main__":
    broker = Broker()
    broker.start()

    id = 0
    it = 0

    while True:

        if it == 1:
            break

        # fetch incidents from HERE
        ti_here = fetch_ti_here()

        if len(ti_here) != 0:

            for incident in ti_here["results"]:
                msg = {
                    "id": id+1,
                    "type": incident['incidentDetails']['type'],
                    "source": "HERE",
                    "sourceid": incident['incidentDetails']['id'],
                    "description": incident['incidentDetails']['description']['value'],
                    "location": incident['location']['shape'],
                    "start": incident['incidentDetails']['startTime'],
                    "end": incident['incidentDetails']['endTime'],
                    "timestamp": ti_here['entryTime']
                }
                print(json.dumps(msg, indent=4))
                id += 1

                Producer = mqtt.Producer()
                topic = "/events"
                status = Producer.publish(json.dumps(msg), topic)

                if status != 0:
                    print("Error publishing message")
                else:
                    print("Message published")

        it += 1
        time.sleep(5)
