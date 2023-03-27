from fastapi import APIRouter
from ..database import Event
from ..serializers.eventSerializers import eventEntity

router = APIRouter()

@router.get("/get_events")
async def get_events():
    # Return all events and serialize them
    return [eventEntity(event) for event in Event.find()]