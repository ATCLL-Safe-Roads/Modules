from bson import ObjectId
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class OID(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not isinstance(v, ObjectId):
            raise TypeError('ObjectId required')
        return str(v)


class EventPoint(BaseModel):
    lat: float
    lng: float


class EventGeometry(BaseModel):
    points: List[EventPoint]
    length: float


class EventSerializer(BaseModel):
    id: OID = Field(alias="_id")
    type: str
    source: str
    sourceid: str
    description: str
    location: str
    geometry: List[EventGeometry]
    start: datetime
    end: datetime
    timestamp: datetime

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if '_id' in data:
            data['id'] = data.pop('_id')
        return data
