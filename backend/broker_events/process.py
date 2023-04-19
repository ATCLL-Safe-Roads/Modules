import json
import time
import datetime
import copy

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


class Flow():
    counter = 0

    def __init__(self, source, location, avgspeed, segments, timestamp):
        self.source = source
        self.location = location
        self.avgspeed = avgspeed
        self.segments = segments
        self.timestamp = timestamp
        Flow.counter += 1


class Processing():
    def __init__(self):
        self.post_ids = {1: "Rua da Pega", 3: "Ponte da Dobadoura", 4: "Rotunda Monumento ao Marnoto e à Salineira",
                         10: "Avenida Dr. Lourenço Peixinho, cruzamento frente à Segurança social",
                         11: "Avenida Dr. Lourenço Peixinho, cruzamento com a Rua do Eng. Oudinot",
                         12: "Avenida Dr. Lourenço Peixinho, entroncamento com a Rua Luis G. Carvalho",
                         14: "Avenida Dr. Lourenço Peixinho, entroncamento com a Rua Luis G. Carvalho",
                         15: "Cais de São Roque", 18: "Rua Combatentes da Grande Guerra",
                         19: "Parque dos Remadores Olímpicos", 21: "Rotunda do Oita", 22: "Cais da Fonte Nova",
                         23: "Rotunda do Hospital", 24: "Quiosque ao lado do Hospital", 25: "Escola da Glória",
                         27: "Sé", 28: "José Estevão", 29: "S. Martinho II", 30: "Avenida 25 de Abril",
                         31: " Dr. Mario Sacramento II", 32: "Convivio", 33: "Rua Doutor Mário Sacramento",
                         35: "Avenida da Universidade", 36: "Rotunda do Pingo Doce", 38: "Parque da CP",
                         39: "Rotunda de Esgueira", 41: "Quartel I", 37: "Rotunda Forca", 40: "Quartel II", 44: "Ria"}
        self.data_gather = {}
        self.transit_counts = {id: 0 for id in self.post_ids}
        self.active_alerts = {}

    def camera_count(self, msg, postID):
        class_count = {}
        camera_response = json.loads(msg)

        if camera_response != []:
            class_label = camera_response['classLabel']
            if class_label in ['person']:
                key = average_class_label_key(postID, class_label)
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
        return class_count

    '''Process the radar traffic data'''

    def radar_traffic(self, msg, postID, heading=0):
        radar_response = json.loads(msg)

        if radar_response != []:
            keys = average_speed_key(postID, heading)
            keyc = average_car_key(postID, heading)
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
                return average_speed / count, vehicleHeavy + vehicleLight
            return average_speed, vehicleHeavy + vehicleLight

    def check_for_traffic(self, postID, speed=0, cars=0, people=0, heading=0):
        if speed == 0 or cars == 0:
            return []

        flow = None
        source = f"ATCLL Sensor SLP{postID}"
        location = self.post_ids[postID]
        heading = "entry" if heading == 1 else "exit"

        print(
            f"{location}:{heading} - Cars: {cars}, Avg Speed: {speed}m/s, People:{people}")

        if speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD and people > NUMBER_OF_PEOPLE_THRESHOLD:
            self.transit_counts[postID] += 1
            print(
                f"Instance {self.transit_counts[postID]} of Traffic Detected at {location}")
            description = f"There is a high amount of traffic at the moment in {location} {heading}"
            level = 3
        elif speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD / 1.5 and people > NUMBER_OF_PEOPLE_THRESHOLD * 1.5:
            self.transit_counts[postID] += 1
            print(
                f"Instance {self.transit_counts[postID]} of Traffic Detected at {location}")
            description = f"There is some traffic at the moment in {location} {heading}"
            level = 1
        elif speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD * 1.5 and people > NUMBER_OF_PEOPLE_THRESHOLD / 2:
            self.transit_counts[postID] += 1
            print(
                f"Instance {self.transit_counts[postID]} of Traffic Detected at {location}")
            description = f"There is some traffic at the moment in {location} {heading}"
            level = 2
        elif speed < AVERAGE_SPEED_THRESHOLD and cars > NUMBER_OF_CARS_THRESHOLD * 1.2:
            self.transit_counts[postID] += 1
            print(
                f"Instance {self.transit_counts[postID]} of Traffic Detected at {location}")
            description = f"There is some traffic at the moment in {location} {heading}"
            level = 1
        else:
            self.transit_counts[postID] = 0

        print(self.transit_counts[postID])

        if self.transit_counts[postID] >= TRANSIT_COUNT_THRESHOLD:
            self.transit_counts[postID] = 0

            '''Don't send alert if it has already been sent in the last <ALERTS_TIME_TO_LIVE> seconds'''
            if f"{postID}:transit" in self.active_alerts.keys() and time.mktime(
                    self.active_alerts[f"{postID}:transit"].timestamp.timetuple()) > time.time() - ALERTS_TIME_TO_LIVE:
                self.active_alerts[f"{postID}:transit"].timestamp = datetime.datetime.now(datetime.timezone(
                    datetime.timedelta(hours=+1)))  # reset the timer to stay with the alert for another 30 minutes
                return []

            f = data["features"]

            coordinates = []

            for i in f:
                if location in i["properties"]["name"]:
                    coordinates += i["geometry"]["coordinates"]

            segments = {
                "points": coordinates,
                "jamFactor": float(level),
            }

            flow = Flow(source, location, speed * 3.6, segments,
                        datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1))).__str__())

            self.active_alerts[f"{postID}:transit"] = copy.deepcopy(flow)
            self.active_alerts[f"{postID}:transit"].timestamp = datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=+1)))

            return [json.dumps(flow.__dict__)]
        return []
