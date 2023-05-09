from datetime import datetime
from fastapi import APIRouter

from ..database import Flow
from ..serializers.flows import FlowSerializer

router = APIRouter()


@router.get('')
async def get_flows(source: str = None, start: str = None, end: str = None):
    query = {}
    if source:
        query['source'] = {'$eq': source}
    if start:
        query['timestamp'] = {'$gte': datetime.fromisoformat(start[:-1])}
    if end:
        query['timestamp'] = {'$lte': datetime.fromisoformat(end[:-1])}
    # Return first occurrence of each location
    locations = set()
    ret = []
    for flow in Flow.find(query):
        if flow['location'] not in locations:
            locations.add(flow['location'])
            ret.append(FlowSerializer(**flow))
    return ret
