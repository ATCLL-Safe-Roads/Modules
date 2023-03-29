import mqtt
import json
import requests
import datetime

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN
INCIDENT_URL = 'https://data.traffic.hereapi.com/v7/incidents'


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
    ti_here = requests.get(url=INCIDENT_URL, params=params).json()

    id = 0
    it = 0

    if len(ti_here) != 0:

        for incident in ti_here["results"]:
            # convert ISO 8601(incident['incidentDetails']['startTime']) to Datetime
            incident['incidentDetails']['startTime'] = datetime.datetime.fromisoformat(incident['incidentDetails']['startTime'])
            incident['incidentDetails']['endTime'] = datetime.datetime.fromisoformat(incident['incidentDetails']['endTime'])

            msg = {
                "id": id+1,
                "type": incident['incidentDetails']['type'],
                "source": "HERE",
                "sourceid": incident['incidentDetails']['id'],
                "description": incident['incidentDetails']['description']['value'],
                "location": incident['location']['shape'],
                "start": incident['incidentDetails']['startTime'],
                "end": incident['incidentDetails']['endTime'],
                "timestamp": incident['incidentDetails']['entryTime']
            }
            print(json.dumps(msg, indent=4, ensure_ascii=False, default=str))
            id += 1

            Producer = mqtt.Producer()
            topic = "/events"
            msg1 = {}
            status = Producer.publish(json.dumps(
                msg, ensure_ascii=False, default=str).encode('utf-8'), topic)

            if status != 0:
                print("Error publishing message")
            else:
                print("Message published")
            return status
