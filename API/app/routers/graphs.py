from datetime import datetime, timedelta
from fastapi import APIRouter
from random import Random
from threading import Thread

from app.database import Event, Flow
from app.open_weather_api_service import OpenWeatherApiService
from app.serializers.graphs import GraphSerializer

router = APIRouter()


def get_labels(start: datetime, end: datetime):
    # Get hour step based on interval
    interval = end - start
    if interval < timedelta(days=1):
        hour_step = 1
    elif interval < timedelta(days=2):
        hour_step = 2
    elif interval < timedelta(days=3):
        hour_step = 3
    elif interval < timedelta(days=4):
        hour_step = 4
    elif interval < timedelta(days=7):
        hour_step = 6
    elif interval < timedelta(days=30):
        hour_step = 24
    elif interval < timedelta(days=60):
        hour_step = 48
    elif interval < timedelta(days=90):
        hour_step = 72  # 3 days
    elif interval < timedelta(days=180):
        hour_step = 168  # 7 days
    elif interval < timedelta(days=365):
        hour_step = 360  # 15 days
    elif interval < timedelta(days=730):
        hour_step = 720  # 30 days
    elif interval < timedelta(days=1095):
        hour_step = 1440  # 60 days
    else:
        hour_step = 2880  # 120 days

    # Get labels with hour step
    labels = [start + timedelta(hours=i) for i in range(0, int(interval.total_seconds() / 3600), hour_step)]

    return labels, hour_step


@router.get('')
async def get_graphs(type: str = None, source: str = None, location: str = None, start: str = None, end: str = None):
    # Sanitize start and end
    if start:
        start = start[:-1] if start[-1] == 'Z' else start
    if end:
        end = end[:-1] if end[-1] == 'Z' else end

    # Convert start and end to datetime
    start_dt = datetime.fromisoformat(start) if start else datetime.now() - timedelta(weeks=1)
    end_dt = datetime.fromisoformat(end) if end else datetime.now()

    # Get labels for graph
    labels, hour_step = get_labels(start_dt, end_dt)

    # Events

    events_query = {}
    if type:
        events_query['type'] = {'$in': type.split(',')}
    if source:
        events_query['source'] = {'$in': source.split(',')}
    if location:
        events_query['location'] = {'$regex': location, '$options': 'i'}
    if start:
        events_query['end'] = {'$gte': start_dt}
    if end:
        events_query['start'] = {'$lte': end_dt}
    events = Event.find(events_query)

    events_data = {}
    for event in events:
        # Initialize data for event type
        if event['type'] not in events_data:
            events_data[event['type']] = [0 for _ in range(len(labels))]
        # Distribute event in labels
        for i in range(len(labels)):
            if event['start'] <= labels[i] < event['end'] + timedelta(hours=hour_step):
                events_data[event['type']][i] += 1

    rand = Random()  # TODO: remove

    # Flow

    flows_query = {}
    if start:
        flows_query['timestamp'] = {'$gte': datetime.fromisoformat(start)}
    if end:
        flows_query['timestamp'] = {'$lte': datetime.fromisoformat(end)}
    flows = Flow.find(flows_query)

    flow_data = {
        'real': [[] for _ in range(len(labels))],
        'predict': [rand.random() for _ in range(len(labels))]  # TODO: change to predict
    }
    for flow in flows:
        # Distribute flow in labels
        for i in range(len(labels)):
            if flow['timestamp'] <= labels[i] < flow['timestamp'] + timedelta(hours=hour_step):
                flow_data['real'][i].append(flow['avgspeed'])
    # Average flow in each label
    flow_data['real'] = [3.6 * sum(avgspeeds) / len(avgspeeds)
                         if len(avgspeeds) > 0 else 0 for avgspeeds in flow_data['real']]

    # Weather

    weather_data = {
        'temperature': [0.0 for _ in range(len(labels))],
        'humidity': [0.0 for _ in range(len(labels))]
    }
    latitude = 40.64427
    longitude = -8.64554
    if hour_step <= 6:
        weather = OpenWeatherApiService.get_history(latitude, longitude, start_dt, 168)
        if 'list' in weather:
            for i in range(len(labels)):
                if i * hour_step >= len(weather['list']):
                    break
                weather_data['temperature'][i] = weather['list'][i * hour_step]['main']['temp'] \
                    if 'cod' in weather and weather['cod'] == '200' else 0.0
                weather_data['humidity'][i] = weather['list'][i * hour_step]['main']['humidity'] \
                    if 'cod' in weather and weather['cod'] == '200' else 0.0
    elif hour_step in {24, 48, 72}:
        j = 0
        while start_dt < end_dt:
            weather = OpenWeatherApiService.get_history(latitude, longitude, start_dt, 168)
            if 'list' in weather:
                k = 0
                for i in range(j, len(labels)):
                    if k * hour_step >= len(weather['list']):
                        break
                    weather_data['temperature'][i] = weather['list'][k * hour_step]['main']['temp'] \
                        if 'cod' in weather and weather['cod'] == '200' else 0.0
                    weather_data['humidity'][i] = weather['list'][k * hour_step]['main']['humidity'] \
                        if 'cod' in weather and weather['cod'] == '200' else 0.0
                    j += 1
                    k += 1
            else:
                j += 168 // hour_step
            start_dt += timedelta(days=7)
    else:
        def fetch_single_weather_data(_i, _latitude, _longitude, _start):
            _weather = OpenWeatherApiService.get_history(_latitude, _longitude, _start, 1)
            weather_data['temperature'][_i] = _weather['list'][0]['main']['temp'] \
                if 'cod' in _weather and _weather['cod'] == '200' else 0.0
            weather_data['humidity'][_i] = _weather['list'][0]['main']['humidity'] \
                if 'cod' in _weather and _weather['cod'] == '200' else 0.0

        tt = []
        for i in range(len(labels)):
            weather_ts = start_dt + timedelta(hours=i * hour_step)
            if hour_step == 24:
                weather_ts = weather_ts.replace(hour=12)
            elif hour_step == 48:
                weather_ts = weather_ts.replace(hour=12)
            elif hour_step == 72:
                weather_ts = weather_ts.replace(hour=12) + timedelta(days=1)
            elif hour_step == 168:
                weather_ts = weather_ts.replace(hour=12) + timedelta(days=3)
            elif hour_step == 360:
                weather_ts = weather_ts.replace(hour=12) + timedelta(days=7)
            elif hour_step == 720:
                weather_ts = weather_ts.replace(hour=12) + timedelta(days=14)
            elif hour_step == 1440:
                weather_ts = weather_ts.replace(hour=12) + timedelta(days=30)
            elif hour_step == 2880:
                weather_ts = weather_ts.replace(hour=12) + timedelta(days=60)
            t = Thread(target=fetch_single_weather_data, args=(i, latitude, longitude, weather_ts))
            tt.append(t)
        # Start all threads
        for t in tt:
            t.start()
        # Wait for all threads to finish
        for t in tt:
            t.join()

    return GraphSerializer(labels=labels, events=events_data, flow=flow_data, weather=weather_data)
