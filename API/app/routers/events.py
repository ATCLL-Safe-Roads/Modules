from datetime import datetime
from fastapi import APIRouter

from ..database import Event
from ..serializers.events import EventSerializer

router = APIRouter()


@router.get('')
async def get_events(type: str = None, source: str = None, location: str = None, start: str = None, end: str = None):
    # Sanitize start and end
    if start:
        start = start[:-1] if start[-1] == 'Z' else start
    if end:
        end = end[:-1] if end[-1] == 'Z' else end

    query = {}
    if type:
        query['type'] = {'$in': type.split(',')}
    if source:
        query['source'] = {'$in': source.split(',')}
    if location:
        query['location'] = {'$regex': location, '$options': 'i'}
    if start:
        query['end'] = {'$gte': datetime.fromisoformat(start)}
    if end:
        query['start'] = {'$lte': datetime.fromisoformat(end)}
    return [EventSerializer(**event) for event in Event.find(query)]


@router.get('/{id}')
async def get_event(id: int):
    return EventSerializer(Event.find_one({'id': id}))
