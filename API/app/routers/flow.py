from datetime import datetime
from fastapi import APIRouter

from ..database import Flow
from ..serializers.flowSerializers import flowEntity

router = APIRouter()

@router.get("/get_flows")
async def get_flows():
    # Return all events and serialize them
    return [flowEntity(flow) for flow in Flow.find()]

@router.get("/get_flow/{id}")
async def get_flow(id: int):
    return flowEntity(Flow.find_one({"id": id}))

@router.get("/get_flows_filtered")
async def get_flows_filtered(source: str = None, start: str = None, end: str = None):
    query = {}
    if start and end:
        ds = datetime.strptime(start, "%Y-%m-%d")
        de = datetime.strptime(end, "%Y-%m-%d")
        query["timestamp"] = {"$gte": ds, "$lte": de}
    if source:
        query["source"] = source
    return [flowEntity(flow) for flow in Flow.find(query)]