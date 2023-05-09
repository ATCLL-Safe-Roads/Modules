from pydantic import BaseModel
from datetime import datetime
from bson import ObjectId


#{
#    "id": "int",
#    "type": "str",
#    "source": "str",
#    "sourceid": "int",
#    "description": "str",
#    "location": "str",
#    "points": "lst",
#    "start": "datetime",
#    "end": "datetime",
#    "timestamp": "datetime"
#}
class EventSchema(BaseModel):
    id: int
    type: str
    source: str
    sourceid: str
    description: str
    location: str
    geometry: list
    start: datetime
    end: datetime
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str}


#{
#    "id": "int",
#    "source": "str",
#    "location": "str",
#    "avgspeed": "float",
#    "segments": [
#        {
#            "jamFactor": "float",
#            "points": [
#                {
#                    "lat": "double",
#                    "lon": "double"
#                },
#                {
#                    "lat": "double",
#                    "lon": "double"
#                },
#                ...
#            ]
#        },
#        ...
#    ],
#    "timestamp": "datetime"
#}


class FlowSchema(BaseModel):
    id: int
    source: str
    location: str
    avgspeed: float
    segments: list
    timestamp: datetime

    class Config:
        json_encoders = {ObjectId: str}