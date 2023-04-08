import mqtt
import json
import requests
import datetime

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'  # REPLACE WITH YOUR OWN
INCIDENT_URL = 'https://data.traffic.hereapi.com/v7/incidents'

cache = []


def get_location(lat,lon):
    params = {
        'apiKey': API_KEY,
        'at': f'{lat},{lon}'
    }
    r = requests.get(url='https://revgeocode.search.hereapi.com/v1/revgeocode', params=params)
    rj = r.json()
    return rj['items'][0]['title']


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

    if len(ti_here) != 0:

        for incident in ti_here["results"]:

            lat = incident['location']['shape']['links'][0]['points'][0]["lat"]
            lon = incident['location']['shape']['links'][0]['points'][0]["lng"]

            location = get_location(lat, lon)

            msg = {
                "type": incident['incidentDetails']['type'],
                "source": "HERE",
                "sourceid": incident['incidentDetails']['id'],
                "description": incident['incidentDetails']['description']['value'],
                "location": location,
                "points": incident['location']['shape']['links'],
                "start": incident['incidentDetails']['startTime'],
                "end": incident['incidentDetails']['endTime'],
                "timestamp": incident['incidentDetails']['entryTime']
            }

            if msg not in cache:
                cache.append(msg)
                # print msg
                print(json.dumps(msg, indent=4, ensure_ascii=False, default=str))
                Producer = mqtt.Producer()
                topic = "/events"
                status = Producer.publish(json.dumps(
                    msg, ensure_ascii=False, default=str).encode('utf-8'), topic)

                if status != 0:
                    print("Error publishing message")
                else:
                    print("Message published")
            else:
                print("Message already in cache")
            #return status
