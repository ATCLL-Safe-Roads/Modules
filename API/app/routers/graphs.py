import requests

from datetime import datetime, timedelta
from fastapi import APIRouter
from random import Random

from app.config import settings
from app.database import Event, Flow
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
    elif interval < timedelta(days=14):
        hour_step = 12
    else:
        hour_step = 24

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
    if source:
        flows_query['source'] = {'$eq': source}
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
                flow_data['real'][i].extend([segment['jam_factor'] for segment in flow['segments']])
    # Average flow in each label
    flow_data['real'] = [sum(jam_factors) / len(jam_factors)
                         if len(jam_factors) > 0 else 0 for jam_factors in flow_data['real']]

    # Weather

    weather_data = {
        'temperature': [[] for _ in range(len(labels))],
        'humidity': [[] for _ in range(len(labels))]
    }

    # TODO: Don't call for every label
    for i in range(len(labels)):
        weather_ts = start_dt + timedelta(hours=i * hour_step)
        if hour_step == 24:
            weather_ts.replace(hour=12, minute=0, second=0, microsecond=0)
        weather_param = {
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lat': 40.64427,
            'lon': -8.64554,
            'start': int(datetime.timestamp(weather_ts)),
            'cnt': 1
        }
        weather = requests.get(url=settings.OPENWEATHER_HISTORY_URL, params=weather_param).json()

        weather_data['temperature'][i] = weather['list'][0]['main']['temp'] if 'cod' in weather and weather['cod'] == '200' else 0
        weather_data['humidity'][i] = weather['list'][0]['main']['humidity'] if 'cod' in weather and weather['cod'] == '200' else 0

    return GraphSerializer(labels=labels, events=events_data, flow=flow_data, weather=weather_data)
