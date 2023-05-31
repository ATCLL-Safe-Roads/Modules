from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.mqtt import mqtt
from app.routers import events, flows, graphs
import sys
import logging

logging.basicConfig(
    level=logging.DEBUG, 
    format='%(asctime)s,%(msecs)03d: %(module)17s->%(funcName)-15s - [%(levelname)7s] - %(message)s',
    handlers=[logging.StreamHandler(stream=sys.stdout)]
)

_SystemLogger = logging.getLogger().getChild('System')

_SystemLogger.info("Successfully imported module")

app = FastAPI()
mqtt.init_app(app)

def custom_openapi():
    openapi_schema = get_openapi(
        title='ATCLL - Safe Roads - API Module',
        version='1.0.0',
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://atcll-data.nap.av.it.pt/static/img/logo.png"
    }
    openapi_schema["paths"]["/events"]["get"]["parameters"][0][
        "description"] = "accident,road_work,congestion,road_hazard,immobilized_vehicle,closed_road,police_presence,floo,pothole,wrong_way"
    openapi_schema["paths"]["/events"]["get"]["parameters"][1][
        "description"] = "here or atcll"
    openapi_schema["paths"]["/events"]["get"]["parameters"][3][
        "description"] = "Start date in format '%Y-%m-%dT%H:%M:%S%z'"
    openapi_schema["paths"]["/events"]["get"]["parameters"][4][
        "description"] = "End date in format '%Y-%m-%dT%H:%M:%S%z'"
    openapi_schema["paths"]["/flows"]["get"]["parameters"][0][
        "description"] = "Start date in format '%Y-%m-%dT%H:%M:%S%z'"
    openapi_schema["paths"]["/flows"]["get"]["parameters"][1][
        "description"] = "End date in format '%Y-%m-%dT%H:%M:%S%z'"
    openapi_schema["paths"]["/graphs"]["get"]["parameters"][0][
        "description"] = "accident,road_work,congestion,road_hazard,immobilized_vehicle,closed_road,police_presence,floo,pothole,wrong_way"
    openapi_schema["paths"]["/graphs"]["get"]["parameters"][1][
        "description"] = "here or atcll"
    openapi_schema["paths"]["/graphs"]["get"]["parameters"][2][
        "description"] = "temperature or humidity or temperature,humidity"
    openapi_schema["paths"]["/graphs"]["get"]["parameters"][4][
        "description"] = "Start date in format '%Y-%m-%dT%H:%M:%S%z'"
    openapi_schema["paths"]["/graphs"]["get"]["parameters"][5][
        "description"] = "End date in format '%Y-%m-%dT%H:%M:%S%z'"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# API Documentation
app.openapi = custom_openapi

# API CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# API Routes
app.include_router(events.router, prefix='/events', tags=['events'])
app.include_router(flows.router, prefix='/flows', tags=['flows'])
app.include_router(graphs.router, prefix='/graphs', tags=['graphs'])
