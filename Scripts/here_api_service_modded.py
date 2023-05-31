import json
import paho.mqtt.client as mqtt
import requests

ATCLL_BROKER_HOST = "atcll-data.nap.av.it.pt"
ATCLL_BROKER_PORT = 1884

HERE_API_KEY = 'Zlw7LEfyrn8dHgcKyoQHDTDMMg8YmSNGWkvptwNS2xU'
HERE_REV_GEOCODE_URL = 'https://revgeocode.search.hereapi.com/v1/revgeocode'

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


class Producer:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.connect(ATCLL_BROKER_HOST, ATCLL_BROKER_PORT)

    def publish(self, message, topic):
        result = self.client.publish(topic, message, retain=True, qos=0)
        status = result[0]
        return status


class HereApiServiceModded:

    def __init__(self):
        self.mqtt_producer = Producer()

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

    def publish_incident_data(self, ti_data):
        # Incidents
        ti_msgs = []

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

        # Publish
        events_status = [self.mqtt_producer.publish(json.dumps(ti_msg).encode('utf-8'), '/events') for ti_msg in
                         ti_msgs]

        print(f'INFO: Published incident data from HERE API - events={"OK" if sum(events_status) == 0 else "ERROR"}')

    def publish_flow_data(self, tf_data):
        # Flows
        tf_msgs = []

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
        flows_status = [self.mqtt_producer.publish(json.dumps(tf_msg).encode('utf-8'), '/flows') for tf_msg in tf_msgs]

        print(f'INFO: Published flow data from HERE API - flows={"OK" if sum(flows_status) == 0 else "ERROR"}')
