import os
import requests
import schedule
import time

from datetime import datetime
from flask import Flask
from threading import Thread

API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'

INCIDENT_URL = 'https://data.traffic.hereapi.com/v7/incidents'
FLOW_URL = 'https://data.traffic.hereapi.com/v7/flow'

app = Flask(__name__)


@app.route('/')
def home():
    return 'Still Alive!'


def get_traffic_incident(latitude, longitude, radius):
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


def get_traffic_flow(latitude, longitude, radius):
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


def grab_here():
    ts_str = datetime.now().replace(microsecond=0).isoformat().replace(':', '-')  # 'YYYY-MM-DDTHH-MM-SS'

    print(f'Grabbing HERE data at {ts_str}')

    # Aveiro
    lat = 40.64427
    lng = -8.64554
    rad = 5000

    ti_data = get_traffic_incident(lat, lng, rad)
    tf_data = get_traffic_flow(lat, lng, rad)

    if not os.path.exists('incident'):
        os.makedirs('incident')
    with open(f'incident/ti_{ts_str}.json', 'w') as f:
        f.write(str(ti_data))

    if not os.path.exists('flow'):
        os.makedirs('flow')
    with open(f'flow/tf_{ts_str}.json', 'w') as f:
        f.write(str(tf_data))


class Scheduler(Thread):

    def __init__(self):
        super().__init__()
        schedule.every().hour.at(':00').do(grab_here)
        schedule.every().hour.at(':30').do(grab_here)

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    # Starts the scheduler
    scheduler = Scheduler()
    scheduler.start()

    # Starts the Flask server
    app.run(host='0.0.0.0', port=8000)


if __name__ == '__main__':
    main()
