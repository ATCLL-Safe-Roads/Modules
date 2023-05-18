import json
import time

from datetime import datetime, timedelta

from mqtt import Producer

AVERAGE_SPEED_THRESHOLD = 8  # m/s
NUMBER_OF_PEOPLE_THRESHOLD = 2
NUMBER_OF_CARS_THRESHOLD = 5
TRANSIT_COUNT_THRESHOLD = 5
ALERTS_TIME_TO_LIVE = 30 * 60  # seconds


class ProcessService:
    def __init__(self, p_ids, p_names, p_points, mqtt_producer: Producer):
        self.p_ids = p_ids
        self.p_names = p_names
        self.p_points = p_points
        self.mqtt_producer = mqtt_producer

        self.aveiro_roads = self.get_aveiro_roads('aveiro_roads.json')

        self.average_speeds = {p_id: 0 for p_id in p_ids}
        self.vehicle_count = {p_id: 0 for p_id in p_ids}
        self.person_count = {p_id: 0 for p_id in p_ids}
        self.transit_counts = {p_id: 0 for p_id in p_ids}

        self.data_gather = {}
        self.active_alerts = {}
        self.last_centers = {}
        self.count = {}

    @staticmethod
    def get_aveiro_roads(fname):
        with open(fname, encoding='utf-8') as f:
            data = json.load(f)
        return data['features']

    def camera_count(self, msg, p_id):
        class_count = {}
        class_label = msg['classLabel']

        if class_label in ['person']:
            key = f'{p_id}:average_{class_label}'
            if key not in self.data_gather:
                self.data_gather[key] = []
            class_count[class_label] = msg['classCount']

            self.data_gather[key].append(f'{class_count[class_label]}:{time.time()}')

            first_data_gather_time = self.data_gather[key][0].split(':')
            if float(first_data_gather_time[1]) + 60 < time.time():
                total = 0
                for speed in self.data_gather[key]:
                    speed = speed.split(':')[0]
                    total += float(speed)
                self.data_gather[key] = [
                    f'{total / len(self.data_gather[key])}:{time.time()}']
        self.person_count[p_id] = class_count['person'] if 'person' in class_count else self.person_count[p_id]

    def radar_traffic(self, msg, p_id, heading=0):
        speed_key = f'{p_id}:average_speed:{heading}'
        vehicle_key = f'{p_id}:average_vehicle:{heading}'
        if speed_key not in self.data_gather.keys():
            self.data_gather[speed_key] = []
        if vehicle_key not in self.data_gather.keys():
            self.data_gather[vehicle_key] = []

        speed_heavy = msg['speedHeavy']
        speed_light = msg['speedLight']
        vehicle_heavy = msg['vehicleHeavy']
        vehicle_light = msg['vehicleLight']

        average_speed = 0.0
        count = 0
        if vehicle_light > 0:
            average_speed += speed_light
            count += 1
        if vehicle_heavy > 0:
            average_speed += speed_heavy
            count += 1

        current_time = time.time()
        self.data_gather[speed_key].append(f'{average_speed / count}:{current_time}') if count != 0 else \
            self.data_gather[speed_key].append(f'0:{current_time}')
        self.data_gather[vehicle_key].append(f'{(vehicle_heavy + vehicle_light):.0f}:{current_time}') if (
                                                                                                                 vehicle_heavy + vehicle_light) != 0 else \
            self.data_gather[vehicle_key].append(f'0:{current_time}')

        # Store the vehicle average speed for each minute
        first_data_gather_time = self.data_gather[speed_key][0].split(':')
        if float(first_data_gather_time[1]) + 60 < current_time:
            total = 0.0
            for speed in self.data_gather[speed_key]:
                speed = speed.split(':')[0]
                total += float(speed)
            self.data_gather[speed_key] = [
                f'{total / len(self.data_gather[speed_key])}:{time.time()}']

            total = 0.0
            for vehicle in self.data_gather[vehicle_key]:
                vehicle = vehicle.split(':')[0]
                total += float(vehicle)
            self.data_gather[vehicle_key] = [
                f'{total / len(self.data_gather[vehicle_key])}:{time.time()}']

        self.average_speeds[f'{p_id}:{heading}'] = average_speed if count == 0 else average_speed / count
        self.vehicle_count[f'{p_id}:{heading}'] = vehicle_heavy + vehicle_light

    def check_for_traffic(self, p_id, heading=None):
        speed = self.average_speeds[p_id] if not heading else self.average_speeds[f'{p_id}:{heading}']
        vehicles = self.vehicle_count[p_id] if not heading else self.vehicle_count[f'{p_id}:{heading}']
        people = self.person_count[p_id] if not heading else self.person_count[f'{p_id}:{heading}']

        if speed == 0 or vehicles == 0:
            return

        self.transit_counts[p_id] += 1
        if speed < AVERAGE_SPEED_THRESHOLD and vehicles > NUMBER_OF_CARS_THRESHOLD and people > NUMBER_OF_PEOPLE_THRESHOLD:
            jf = 3
        elif speed < AVERAGE_SPEED_THRESHOLD and vehicles > NUMBER_OF_CARS_THRESHOLD * 1.5 and people > NUMBER_OF_PEOPLE_THRESHOLD / 2:
            jf = 2
        elif speed < AVERAGE_SPEED_THRESHOLD and vehicles > NUMBER_OF_CARS_THRESHOLD / 1.5 and people > NUMBER_OF_PEOPLE_THRESHOLD * 1.5:
            jf = 1
        elif speed < AVERAGE_SPEED_THRESHOLD and vehicles > NUMBER_OF_CARS_THRESHOLD * 1.2:
            jf = 1
        else:
            self.transit_counts[p_id] = 0
            return

        if self.transit_counts[p_id] >= TRANSIT_COUNT_THRESHOLD:
            self.transit_counts[p_id] = 0

            # Don't send alert if it has already been sent in the last ALERTS_TIME_TO_LIVE seconds
            if f'{p_id}:transit' in self.active_alerts \
                    and (datetime.now() - self.active_alerts[f'{p_id}:transit']).seconds < ALERTS_TIME_TO_LIVE:
                return

            points = []
            for road in self.aveiro_roads:
                if self.p_names[p_id] in road['properties']['name']:
                    for coords in road['geometry']['coordinates']:
                        points.append({
                            'lat': coords[1],
                            'lng': coords[0]
                        })

            now_ts = datetime.now()
            msg = {
                'source': 'atcll',
                'location': self.p_names[p_id],
                'avgspeed': speed * 3.6,
                'segments': [{'jam_factor': jf, 'geometry': [{'points': points, 'length': 0}]}],
                'timestamp': str(now_ts.replace(microsecond=0).isoformat()) + 'Z'
            }

            self.active_alerts[f'{p_id}:transit'] = now_ts

            self.mqtt_producer.publish(json.dumps(msg).encode('utf-8'), '/flows')

    def check_wrong_way(self, message, p_id):
        if p_id != 33:
            return

        # Bombeiros -> Glicinias
        p1 = (40.632451, -8.648471)
        p2 = (40.631123, -8.648268)

        # Glicinias -> Bombeiros
        p3 = (40.632452, -8.648500)
        p4 = (40.631359, -8.648343)

        def bg(x):
            return (p2[0] - p1[0]) * (x[1] - p1[1]) - (x[0] - p1[0]) * (p2[1] - p1[1])

        def gb(x):
            return (p4[0] - p3[0]) * (x[1] - p3[1]) - (x[0] - p3[0]) * (p4[1] - p3[1])

        lat = message['latitude']
        lon = message['longitude']
        vehicle_id = message['radarVehicleID']
        heading = message['heading']

        c = (lat, lon)

        if vehicle_id in self.last_centers:
            last_x, last_y = self.last_centers[vehicle_id]

            if abs(last_x - lat) > 0.00008:
                if heading < 0:
                    if bg(c) > 0 and last_x < lat:  # Positive
                        if vehicle_id not in self.count:
                            self.count[vehicle_id] = 1
                        else:
                            self.count[vehicle_id] += 1
                    elif bg(c) < 0 and last_x > lat:  # Negative
                        if vehicle_id not in self.count:
                            self.count[vehicle_id] = 1
                        else:
                            self.count[vehicle_id] += 1
                    else:
                        if vehicle_id in self.count:
                            del self.count[vehicle_id]
                else:
                    if gb(c) > 0 and last_x < lat:  # Positive
                        if vehicle_id not in self.count:
                            self.count[vehicle_id] = 1
                        else:
                            self.count[vehicle_id] += 1
                    elif gb(c) < 0 and last_x > lat:  # Negative
                        if vehicle_id not in self.count:
                            self.count[vehicle_id] = 1
                        else:
                            self.count[vehicle_id] += 1
                    else:
                        if vehicle_id in self.count:
                            del self.count[vehicle_id]

                if vehicle_id in self.count and self.count[vehicle_id] > 5:  # Consecutive wrong way detections
                    now_ts = datetime.now()
                    msg = {
                        'type': 'wrong_way',
                        'source': 'atcll',
                        'sourceid': '0',
                        'description': f'Detected vehicle driving in the wrong way near SLP with id {p_id}.',
                        'location': self.p_names[p_id],
                        'geometry': [{'points': [{'lat': lat, 'lng': lon}]}],
                        'start': str(now_ts.replace(microsecond=0).isoformat()) + 'Z',
                        'end': str((now_ts + timedelta(seconds=30)).replace(microsecond=0).isoformat()) + 'Z',
                        'timestamp': str(now_ts.replace(microsecond=0).isoformat()) + 'Z'
                    }
                    print(f'INFO: {msg["description"]}')

                    events_status = self.mqtt_producer.publish(json.dumps(msg).encode('utf-8'), '/events')
                    print(f'INFO: Published wrong_way event from ATCLL - '
                          f'events={"OK" if events_status == 0 else "ERROR"}')

                    del self.count[vehicle_id]

                self.last_centers[vehicle_id] = (lat, lon)
        else:
            self.last_centers[vehicle_id] = (lat, lon)
