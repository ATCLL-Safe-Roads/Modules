import json
import time
import datetime
import copy

from mqtt import Producer

AVERAGE_SPEED_THRESHOLD = 8  # m/s
NUMBER_OF_PEOPLE_THRESHOLD = 2
NUMBER_OF_CARS_THRESHOLD = 5
TRANSIT_COUNT_THRESHOLD = 5
ALERTS_TIME_TO_LIVE = 30 * 60  # seconds

data = None
with open('aveiro_roads.json', encoding='utf-8') as f:
    data = json.load(f)


def average_speed_key(postID, heading):
    return f"{postID}:average_speed:{heading}"


def average_car_key(postID, heading):
    return f"{postID}:average_car:{heading}"


def average_class_label_key(postID, class_label):
    return f"{postID}:average_{class_label}"


class ProcessService:
    def __init__(self, p_ids, p_names, p_points, mqtt_producer: Producer):
        self.p_ids = p_ids
        self.p_names = p_names
        self.p_points = p_points
        self.mqtt_producer = mqtt_producer

        self.average_speeds = {p_id: 0 for p_id in p_ids}
        self.car_count = {p_id: 0 for p_id in self.p_ids}
        self.person_count = {p_id: 0 for p_id in self.p_ids}

        self.data_gather = {}
        self.transit_counts = {id: 0 for id in self.p_names}
        self.active_alerts = {}
        self.last_centers = {}
        self.count = {}

    def camera_count(self, msg, p_id):
        class_count = {}
        camera_response = json.loads(msg)

        if camera_response != []:
            class_label = camera_response['classLabel']
            if class_label in ['person']:
                key = average_class_label_key(p_id, class_label)
                if key not in self.data_gather.keys():
                    self.data_gather[key] = []
                class_count[class_label] = camera_response['classCount']

                self.data_gather[key].append(
                    f"{class_count[class_label]}:{time.time()}")

                first_data_gather_time = self.data_gather[key][0].split(":")
                if float(first_data_gather_time[1]) + 60 < time.time():
                    sum = 0
                    for speed in self.data_gather[key]:
                        speed = speed.split(':')[0]
                        sum += float(speed)
                    self.data_gather[key] = [
                        f"{sum / len(self.data_gather[key])}:{time.time()}"]
        self.person_count[p_id] = class_count['person'] if 'person' in class_count else self.person_count[p_id]

    '''Process the radar traffic data'''

    def radar_traffic(self, msg, p_id, heading=0):
        radar_response = json.loads(msg)

        if radar_response != []:
            keys = average_speed_key(p_id, heading)
            keyc = average_car_key(p_id, heading)
            if keys not in self.data_gather.keys():
                self.data_gather[keys] = []
            if keyc not in self.data_gather.keys():
                self.data_gather[keyc] = []

            speedHeavy = radar_response['speedHeavy']
            speedLight = radar_response['speedLight']
            vehicleHeavy = radar_response['vehicleHeavy']
            vehicleLight = radar_response['vehicleLight']

            average_speed = 0.0
            count = 0
            if vehicleLight > 0:
                average_speed += speedLight
                count += 1
            if vehicleHeavy > 0:
                average_speed += speedHeavy
                count += 1

            current_time = time.time()
            self.data_gather[keys].append(f"{average_speed / count}:{current_time}") if count != 0 else \
                self.data_gather[keys].append(f"0:{current_time}")
            self.data_gather[keyc].append(f"{(vehicleHeavy + vehicleLight):.0f}:{current_time}") if (
                                                                                                            vehicleHeavy + vehicleLight) != 0 else \
                self.data_gather[keyc].append(f"0:{current_time}")

            # Store the vehicle average speed for each minute
            first_data_gather_time = self.data_gather[keys][0].split(":")
            if float(first_data_gather_time[1]) + 60 < current_time:
                sum = 0
                for speed in self.data_gather[keys]:
                    speed = speed.split(':')[0]
                    sum += float(speed)
                self.data_gather[keys] = [
                    f"{sum / len(self.data_gather[keys])}:{time.time()}"]

                sum = 0
                for car in self.data_gather[keyc]:
                    car = car.split(':')[0]
                    sum += float(car)
                self.data_gather[keyc] = [
                    f"{sum / len(self.data_gather[keyc])}:{time.time()}"]

            if count != 0:
                self.average_speeds[f'{p_id}:{heading}'] = average_speed / count
                self.car_count[f'{p_id}:{heading}'] = vehicleHeavy + vehicleLight
            self.average_speeds[f'{p_id}:{heading}'] = average_speed
            self.car_count[f'{p_id}:{heading}'] = vehicleHeavy + vehicleLight

    def check_for_traffic(self, p_id, heading=None):
        speed = self.average_speeds[p_id] if not heading else self.average_speeds[f'{p_id}:{heading}']
        cars = self.car_count[p_id] if not heading else self.car_count[f'{p_id}:{heading}']
        people = self.person_count[p_id] if not heading else self.person_count[f'{p_id}:{heading}']

        if speed == 0 or cars == 0:
            return []

        flow = None
        source = f"atcll"
        location = self.p_names[p_id]
        heading = "entry" if heading == 1 else "exit"

        # print(f"{location}:{heading} - Cars: {cars}, Avg Speed: {speed}m/s, People:{people}")

        if speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD and people > NUMBER_OF_PEOPLE_THRESHOLD:
            self.transit_counts[p_id] += 1
            print(
                f"Instance {self.transit_counts[p_id]} of Traffic Detected at {location}")
            description = f"There is a high amount of traffic at the moment in {location} {heading}"
            level = 3
        elif speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD / 1.5 and people > NUMBER_OF_PEOPLE_THRESHOLD * 1.5:
            self.transit_counts[p_id] += 1
            print(
                f"Instance {self.transit_counts[p_id]} of Traffic Detected at {location}")
            description = f"There is some traffic at the moment in {location} {heading}"
            level = 1
        elif speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD * 1.5 and people > NUMBER_OF_PEOPLE_THRESHOLD / 2:
            self.transit_counts[p_id] += 1
            print(
                f"Instance {self.transit_counts[p_id]} of Traffic Detected at {location}")
            description = f"There is some traffic at the moment in {location} {heading}"
            level = 2
        elif speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD * 1.2:
            self.transit_counts[p_id] += 1
            print(
                f"Instance {self.transit_counts[p_id]} of Traffic Detected at {location}")
            description = f"There is some traffic at the moment in {location} {heading}"
            level = 1
        else:
            self.transit_counts[p_id] = 0

        # print(self.transit_counts[postID])

        if self.transit_counts[p_id] >= TRANSIT_COUNT_THRESHOLD:
            self.transit_counts[p_id] = 0

            '''Don't send alert if it has already been sent in the last <ALERTS_TIME_TO_LIVE> seconds'''
            if f"{p_id}:transit" in self.active_alerts.keys() and time.mktime(
                    self.active_alerts[f"{p_id}:transit"].timestamp.timetuple()) > time.time() - ALERTS_TIME_TO_LIVE:
                self.active_alerts[f"{p_id}:transit"].timestamp = datetime.datetime.now(datetime.timezone(
                    datetime.timedelta(hours=+1)))  # reset the timer to stay with the alert for another 30 minutes
                return []

            f = data["features"]

            coordinates = []

            for i in f:
                if location in i["properties"]["name"]:
                    coordinates += i["geometry"]["coordinates"]

            coordinatesf = []

            for c in coordinates:
                t = {}
                t["lat"] = c[1]
                t["lng"] = c[0]
                coordinatesf.append(t)

            segments = {
                "jam_factor": float(level),
                "geometry": [{"points": coordinatesf, 'length': 0}],
            }

            flow = Flow(source, location, speed * 3.6, [segments],
                        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1))).__str__())

            self.active_alerts[f"{p_id}:transit"] = copy.deepcopy(flow)
            self.active_alerts[f"{p_id}:transit"].timestamp = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=+1)))

            for flow in [json.dumps(flow.__dict__)]:
                if flow:
                    self.mqtt_producer.publish(flow, '/flows')

    def check_wrong_way(self, message):

        events = []

        # Sentido Bombeiros -> Glicinias
        p1 = (40.632451, -8.648471)
        p2 = (40.631123, -8.648268)

        # Sentido Glicinias -> Bombeiros
        p3 = (40.632452, -8.648500)
        p4 = (40.631359, -8.648343)

        def bg(x):
            return (p2[0] - p1[0]) * (x[1] - p1[1]) - (x[0] - p1[0]) * (p2[1] - p1[1])

        def gb(x):
            return (p4[0] - p3[0]) * (x[1] - p3[1]) - (x[0] - p3[0]) * (p4[1] - p3[1])

        lat = message['latitude']
        lon = message['longitude']
        radarID = message['radarVehicleID']
        heading = message['heading']

        c = (lat, lon)

        if radarID in self.last_centers:
            last_x, last_y = self.last_centers[radarID]

            if abs(last_x - lat) > 8.100000000155205e-05:
                if heading < 0:
                    if bg(c) > 0 and last_x < lat:  # Positivo
                        print(f'car with id={radarID} driving in the wrong way')
                        print(message)
                        if radarID not in self.count:
                            self.count[radarID] = 1
                        else:
                            self.count[radarID] += 1
                    elif bg(c) < 0 and last_x > lat:  # Negativo
                        print(f'car with id={radarID} driving in the wrong way')
                        print(message)
                        if radarID not in self.count:
                            self.count[radarID] = 1
                        else:
                            self.count[radarID] += 1
                    else:
                        if radarID in self.count:
                            del self.count[radarID]
                else:
                    if gb(c) > 0 and last_x < lat:  # Positivo
                        print(f'car with id={radarID} driving in the wrong way')
                        print(message)
                        if radarID not in self.count:
                            self.count[radarID] = 1
                        else:
                            self.count[radarID] += 1
                    elif gb(c) < 0 and last_x > lat:  # Negativo
                        print(f'car with id={radarID} driving in the wrong way')
                        print(message)
                        if radarID not in self.count:
                            self.count[radarID] = 1
                        else:
                            self.count[radarID] += 1
                    else:
                        if radarID in self.count:
                            del self.count[radarID]

                if radarID in self.count and self.count[radarID] > 5:
                    print(f'car with id={radarID} driving in the wrong way 5 TIMES')

                    date = datetime.datetime.now()

                    print(date.replace(microsecond=0).isoformat().__str__() + "Z")

                    date1 = date + datetime.timedelta(seconds=30)

                    print(date1.replace(microsecond=0).isoformat().__str__() + "Z")

                    e = Event("wrong_way", "atcll", "Wrong way", self.p_names[33],
                              [{'points': [{"lat": lat, "lng": lon}]}], date,
                              date1, date)
                    events.append(json.dumps(e.__dict__))

                    del self.count[radarID]

                self.last_centers[radarID] = (lat, lon)
        else:
            self.last_centers[radarID] = (lat, lon)

        for event in events:
            if event:
                self.mqtt_producer.publish(event, '/events')
