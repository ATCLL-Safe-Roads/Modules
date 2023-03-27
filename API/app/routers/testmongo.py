from fastapi import APIRouter
from pymongo.errors import ConnectionFailure
from ..database import client, Event
from datetime import datetime
from ..serializers.eventSerializers import eventEntity

router = APIRouter()

@router.get("/testmongo")
async def test_mongo():
    try:
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
    except ConnectionFailure:
        print("Server not available")
    return "OK"

#{
#    "type": "str",
#    "source": "str",
#    "description": "str",
#    "location": "str",
#    "start": "datetime",
#    "end": "datetime",
#    "timestamp": "datetime"
#}

@router.get("/testmongo2")
async def test_mongo2():
    Event.insert_one(
        {"type": "incident", "source": "here", "description": "test", "location": "test", "start": datetime.now(), "end": datetime.now(), "timestamp": datetime.now() }
    )
    return "OK"

@router.get("/testmongo3")
async def test_mongo3():
    event = eventEntity(Event.find_one({"type": "incident"}))
    return event
