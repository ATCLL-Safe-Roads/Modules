import os

import mqtt
import json
import requests

from dotenv import load_dotenv

load_dotenv()

HERE_API_KEY = os.getenv('HERE_API_KEY')
HERE_INCIDENT_URL = os.getenv('HERE_INCIDENT_URL')
HERE_REV_GEOCODE_URL = os.getenv('HERE_REV_GEOCODE_URL')

TYPE = {
    'accident': 'accident',
    'construction': 'road_work',
    'congestion': 'congestion',
    'disabledVehicle': 'immobilized_vehicle',
    'roadClosure': 'closed_road',
    'roadHazard': 'road_hazard'
}

cache = []


def get_location(lat, lon):
    params = {
        'apiKey': HERE_API_KEY,
        'at': f'{lat},{lon}'
    }
    r = requests.get(url=HERE_REV_GEOCODE_URL, params=params)
    rj = r.json()
    return rj['items'][0]['title']


def fetch_ti_here():
    # Aveiro
    lat = 40.64427
    lon = -8.64554
    rad = 5000  # meters

    params = {
        'apiKey': HERE_API_KEY,
        'locationReferencing': 'shape',
        'in': f'circle:{lat},{lon};r={rad}'
    }
    ti_here = requests.get(url=HERE_INCIDENT_URL, params=params).json()

    if len(ti_here) != 0:

        for incident in ti_here["results"]:

            if incident['incidentDetails']['type'] not in TYPE.keys():
                continue

            lat = incident['location']['shape']['links'][0]['points'][0]["lat"]
            lon = incident['location']['shape']['links'][0]['points'][0]["lng"]

            location = get_location(lat, lon)

            msg = {
                "type": TYPE[incident['incidentDetails']['type']],
                "source": "here",
                "sourceid": incident['incidentDetails']['id'],
                "description": incident['incidentDetails']['description']['value'],
                "location": location,
                "geometry": incident['location']['shape']['links'],
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
            # return status
