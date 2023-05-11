from datetime import datetime, timedelta
from fastapi import APIRouter
from random import Random

from app.database import Event
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
    start = start[:-1] if start[-1] == 'Z' else start
    end = end[:-1] if end[-1] == 'Z' else end

    # Convert start and end to datetime
    start_dt = datetime.fromisoformat(start) if start else datetime.now() - timedelta(weeks=1)
    end_dt = datetime.fromisoformat(end) if end else datetime.now()

    # Get labels for graph
    labels, hour_step = get_labels(start_dt, end_dt)

    # Get events
    query = {}
    if type:
        query['type'] = {'$in': type.split(',')}
    if source:
        query['source'] = {'$in': source.split(',')}
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if start:
        query['end'] = {'$gte': start_dt}
    if end:
        query['start'] = {'$lte': end_dt}
    events = Event.find(query)

    # Get events data for graph
    events_data = {}
    for event in events:
        # Initialize data for event type
        if event['type'] not in events_data:
            events_data[event['type']] = [0 for _ in range(len(labels))]
        # Distribute event in labels
        for i in range(len(labels)):
            if event['start'] <= labels[i] < event['end'] + timedelta(hours=hour_step):
                events_data[event['type']][i] += 1

    rand = Random()

    # Get flow data for graph - TODO: Get real data
    flow_data = {}
    flow_data['real'] = [rand.random() for _ in range(len(labels))]
    flow_data['predict'] = [rand.random() for _ in range(len(labels))]

    # Get weather data for graph - TODO: Get real data
    weather_data = {}
    weather_data['temperature'] = [rand.random() for _ in range(len(labels))]
    weather_data['humidity'] = [rand.random() for _ in range(len(labels))]

    return GraphSerializer(labels=labels, events=events_data, flow=flow_data, weather=weather_data)
