from fastapi import APIRouter
import requests
import json

API_KEY = "D1HKaNOGDTsmzSp0wOHGVlO6CMGekt3o7cSppMAj3Jk"

FLOW_URL = 'https://data.traffic.hereapi.com/v7/flow'
INCIDENT_URL = 'https://data.traffic.hereapi.com/v7/incidents'

LAT = 40.64427
Lon = -8.64554
RAD = 500

router = APIRouter()

idf = 0
idi = 0


@router.get("/get_traffic_flow")
async def get_traffic_flow():
    return get_traffic_flow_HERE(LAT, Lon, RAD)


@router.get("/get_traffic_incident")
async def get_traffic_incident():
    return get_traffic_incident_HERE(LAT, Lon, RAD)


def get_traffic_flow_HERE(latitude, longitude, radius):
    """
    Get traffic flow data from HERE Traffic API v7
    :param latitude: Latitude
    :param longitude: Longitude
    :param radius: Radius in meters
    :return: JSON data
    """
    params = {
        'apiKey': API_KEY,
        'locationReferencing': 'shape',
        'in': f'circle:{latitude},{longitude};r={radius}'
    }
    r = requests.get(url=FLOW_URL, params=params)
    rj = r.json()

    # Parse the data into the structure we want

    if len(rj) != 0:

        lst = []

        global idf

        for flow in rj["results"]:

            if "subSegments" in flow['currentFlow']:

                subSegments = flow['currentFlow']['subSegments']
                shapes = flow['location']['shape']['links']

                msg = {
                    "id": idf + 1,
                    "source": "HERE",
                    "location": flow['location']['description'],
                    "avgspeed": flow['currentFlow']['speedUncapped'],
                    "length": flow['location']['length'],
                    "segments": get_segments(subSegments, shapes),
                    "timestamp": rj['sourceUpdated']
                }
                idf += 1
                lst.append(msg)
            else:
                s = {
                    "speed": flow['currentFlow']['speedUncapped'] * 3.6,
                    "jamFactor": flow['currentFlow']['jamFactor'],
                    "length": flow['location']['length'],
                    "points": flow['location']['shape']['links']
                }

                msg = {
                    "id": idf + 1,
                    "source": "HERE",
                    "location": flow['location']['description'],
                    "avgspeed": flow['currentFlow']['speedUncapped'],
                    "length": flow['location']['length'],
                    "segments": [s],
                    "timestamp": rj['sourceUpdated']
                }
                idf += 1
                lst.append(msg)
        return lst


def get_traffic_incident_HERE(latitude, longitude, radius):
    """
    Get traffic incident data from HERE Traffic API v7
    :param latitude: Latitude
    :param longitude: Longitude
    :param radius: Radius in meters
    :return: JSON data
    """
    params = {
        'apiKey': API_KEY,
        'locationReferencing': 'shape',
        'in': f'circle:{latitude},{longitude};r={radius}'
    }
    r = requests.get(url=INCIDENT_URL, params=params)
    rj = r.json()

    # Parse the data into the structure we want

    if len(rj) != 0:

        global idi

        lst = []

        for incident in rj["results"]:
            msg = {
                "id": idi + 1,
                "type": incident['incidentDetails']['type'],
                "source": "HERE",
                "sourceid": incident['incidentDetails']['id'],
                "description": incident['incidentDetails']['description']['value'],
                "location": incident['location']['shape'],
                "start": incident['incidentDetails']['startTime'],
                "end": incident['incidentDetails']['endTime'],
                "timestamp": rj['sourceUpdated']
            }
            idi += 1
            lst.append(msg)

    return lst


def get_segments(subsegments, shapes):
    segments = []

    for seg in subsegments:
        length = seg["length"]

        lp = []

        lt = 0
        while lt < length:
            if len(shapes) == 0:
                break
            # Check if the next length passes the segment
            if lt + shapes[0]["length"] > length + 5:
                if len(shapes) == 1:
                    # If it's the last shape, just add it
                    lp.append(shapes[0])
                break
            pr = shapes.pop(0)
            lp.append(pr)
            lt += pr["length"]

        msg = {
            "speed": seg["speedUncapped"] * 3.6,
            "jamFactor": seg["jamFactor"],
            "length": length,
            "points": lp
        }

        segments.append(msg)
    return segments
