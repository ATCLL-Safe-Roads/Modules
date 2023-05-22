import json
import os
import requests

from dotenv import load_dotenv

from mqtt import Producer

load_dotenv()

HERE_API_KEY = os.getenv('HERE_API_KEY')
HERE_FLOW_URL = os.getenv('HERE_FLOW_URL')
HERE_INCIDENT_URL = os.getenv('HERE_INCIDENT_URL')
HERE_REV_GEOCODE_URL = os.getenv('HERE_REV_GEOCODE_URL')

TYPE_FROM_HERE = {
    'accident': 'accident',
    'construction': 'road_work',
    'congestion': 'congestion',
    'disabledVehicle': 'immobilized_vehicle',
    'massTransit': None,
    'plannedEvent': None,
    'roadHazard': 'road_hazard',
    'roadClosure': 'closed_road',
    'weather': None,
    'laneRestriction': None,
    'other': None
}


class HereApiService:

    def __init__(self, latitude: float, longitude: float, radius: int, mqtt_producer: Producer):
        self.latitude = latitude
        self.longitude = longitude
        self.radius = radius
        self.mqtt_producer = mqtt_producer

    @staticmethod
    def get_traffic_incident(latitude, longitude, radius):
        """
        Get traffic incident data from HERE Traffic API v7
        :param latitude: Latitude
        :param longitude: Longitude
        :param radius: Radius in meters
        :return: JSON data
        """
        params = {
            'apiKey': HERE_API_KEY,
            'locationReferencing': 'shape',
            'in': f'circle:{latitude},{longitude};r={radius}'
        }
        r = requests.get(url=HERE_INCIDENT_URL, params=params)
        return r.json()

    @staticmethod
    def get_traffic_flow(latitude, longitude, radius):
        """
        Get traffic flow data from HERE Traffic API v7
        :param latitude: Latitude
        :param longitude: Longitude
        :param radius: Radius in meters
        :return: JSON data
        """
        params = {
            'apiKey': HERE_API_KEY,
            'locationReferencing': 'shape',
            'in': f'circle:{latitude},{longitude};r={radius}'
        }
        r = requests.get(url=HERE_FLOW_URL, params=params)
        return r.json()

    @staticmethod
    def get_rev_geocode(latitude, longitude):
        """
        Get reverse geocoding data from HERE Geocoding & Search API v7
        :param latitude: Latitude
        :param longitude: Longitude
        :return: JSON data
        """
        params = {
            'apiKey': HERE_API_KEY,
            'at': f'{latitude},{longitude}'
        }
        r = requests.get(url=HERE_REV_GEOCODE_URL, params=params)
        return r.json()

    @staticmethod
    def __get_segments(flow):
        segments = []

        if 'subSegments' in flow['currentFlow']:
            sub_segments = flow['currentFlow']['subSegments']
            links = flow['location']['shape']['links']

            for s in sub_segments:
                s_len = s['length']

                lp = []
                lt = 0
                while lt < s_len:
                    if len(links) == 0:
                        break
                    # Check if the next length passes the segment
                    if lt + links[0]['length'] > s_len + 5:
                        if len(links) == 1:
                            # If it's the last shape, just add it
                            lp.append(links[0])
                        break
                    pr = links.pop(0)
                    lp.append(pr)
                    lt += pr['length']

                # Calculate jam factor
                s_jf = s['jamFactor']
                if s_jf <= 10 / 3:
                    jf = 1.0
                elif s_jf <= 20 / 3:
                    jf = 2.0
                else:
                    jf = 3.0

                segments.append({
                    'jam_factor': jf,
                    'geometry': lp
                })
        else:
            # Calculate jam factor
            s_jf = flow['currentFlow']['jamFactor']
            if s_jf <= 10 / 3:
                jf = 1.0
            elif s_jf <= 20 / 3:
                jf = 2.0
            else:
                jf = 3.0

            segments = [{
                'jam_factor': jf,
                'geometry': flow['location']['shape']['links']
            }]
        return segments

    def fetch_and_publish_data(self):
        # Incidents
        ti_msgs = []

        ti_data = self.get_traffic_incident(self.latitude, self.longitude, self.radius)

        if 'results' in ti_data:
            for incident in ti_data['results']:
                # Skip unsupported types
                if not TYPE_FROM_HERE[incident['incidentDetails']['type']]:
                    continue

                # Skip if there are no coordinates
                if incident.get('location', {}).get('shape', {}).get('links', [{}])[0].get('points', [{}])[0].get(
                        'lat') is None or \
                        incident.get('location', {}).get('shape', {}).get('links', [{}])[0].get('points', [{}])[0].get(
                            'lng') is None:
                    continue

                # Reverse geocode to find location
                latitude = incident['location']['shape']['links'][0]['points'][0]['lat']
                longitude = incident['location']['shape']['links'][0]['points'][0]['lng']
                location = self.get_rev_geocode(latitude, longitude)

                msg = {
                    'type': TYPE_FROM_HERE[incident['incidentDetails']['type']],
                    'source': 'here',
                    'sourceid': incident['incidentDetails']['id'],
                    'description': incident['incidentDetails']['description']['value'],
                    'location': location['items'][0]['title'],
                    'geometry': incident['location']['shape']['links'],
                    'start': incident['incidentDetails']['startTime'],
                    'end': incident['incidentDetails']['endTime'],
                    'timestamp': incident['incidentDetails']['entryTime']
                }
                ti_msgs.append(msg)

        # Flows
        tf_msgs = []

        tf_data = self.get_traffic_flow(self.latitude, self.longitude, self.radius)

        if 'results' in tf_data:
            for flow in tf_data['results']:
                msg = {
                    'source': 'here',
                    'location': flow['location'].get('description', ''),
                    'avgspeed': flow['currentFlow']['speedUncapped'],
                    'segments': self.__get_segments(flow),
                    'timestamp': tf_data['sourceUpdated']
                }
                tf_msgs.append(msg)

        # Publish
        events_status = [self.mqtt_producer.publish(json.dumps(ti_msg).encode('utf-8'), '/events') for ti_msg in ti_msgs]
        flows_status = [self.mqtt_producer.publish(json.dumps(tf_msg).encode('utf-8'), '/flows') for tf_msg in tf_msgs]

        print(f'INFO: Fetched and published data from HERE API - events={"OK" if sum(events_status) == 0 else "ERROR"}, '
              f'flows={"OK" if sum(flows_status) == 0 else "ERROR"}')

