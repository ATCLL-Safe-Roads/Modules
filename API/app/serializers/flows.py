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


class FlowPoint(BaseModel):
    lat: float
    lng: float


class FlowGeometry(BaseModel):
    points: List[FlowPoint]
    length: float


class FlowSegment(BaseModel):
    geometry: List[FlowGeometry]
    jam_factor: float


class FlowSerializer(BaseModel):
    id: OID = Field(alias="_id")
    source: str
    location: str
    avgspeed: float
    segments: List[FlowSegment]
    timestamp: datetime

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        if '_id' in data:
            data['id'] = data.pop('_id')
        return data
