from datetime import datetime

from fastapi import APIRouter
from ..database import Event
from ..serializers.eventSerializers import eventEntity


router = APIRouter()


@router.get("/get_events")
async def get_events():
    # Return all events and serialize them
    return [eventEntity(event) for event in Event.find()]


@router.get("/get_event/{id}")
async def get_event(id: int):
    # Return the event with the given id and serialize it
    return eventEntity(Event.find_one({"id": id}))


@router.get("/get_events_filtered")
async def get_events_filtered(type: str = None, source: str = None, location: str = None, start: str = None,
                              end: str = None):
    # Return all events that match the given filters and serialize them
    query = {}
    if type:
        query["type"] = type
    if source:
        query["source"] = source
    if location:
        query["location"] = location
    if start and end:
        ds = datetime.strptime(start, "%Y-%m-%d")
        de = datetime.strptime(end, "%Y-%m-%d")
        query["start"] = {"$gte": de}
        query["end"] = {"$lte": ds}
    return [eventEntity(event) for event in Event.find(query)]
