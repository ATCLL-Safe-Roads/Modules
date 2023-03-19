from fastapi import APIRouter
import requests

API_KEY = "D1HKaNOGDTsmzSp0wOHGVlO6CMGekt3o7cSppMAj3Jk"

FLOW_URL = 'https://data.traffic.hereapi.com/v7/flow'
INCIDENT_URL = 'https://data.traffic.hereapi.com/v7/incidents'

LAT = 40.64427
Lon = -8.64554
RAD = 500

router = APIRouter()


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
    return r.json()


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
    return r.json()
