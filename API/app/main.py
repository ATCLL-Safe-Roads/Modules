from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import here, testmongo, events, flow
from app.mqtt import mqtt
from fastapi.openapi.utils import get_openapi

app = FastAPI()

# Connect to MQTT broker

mqtt.init_app(app)

#Add OpenAPI tags
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ATCLL-Data",
        version="1.0.0",
        description="ATCLL-Data API",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://atcll-data.nap.av.it.pt/static/img/logo.png"
    }
    # Add Description to parameter start in endpoint /events/get_events_filtered
    openapi_schema["paths"]["/events/get_events_filtered"]["get"]["parameters"][3]["description"] = "Start date in format YYYY-MM-DD"
    # Add Description to parameter end in endpoint /events/get_events_filtered
    openapi_schema["paths"]["/events/get_events_filtered"]["get"]["parameters"][4]["description"] = "End date in format YYYY-MM-DD"
    # Add Description to parameter start in endpoint /flows/get_flows_filtered
    openapi_schema["paths"]["/flows/get_flows_filtered"]["get"]["parameters"][1]["description"] = "Start date in format YYYY-MM-DD"
    # Add Description to parameter end in endpoint /flows/get_flows_filtered
    openapi_schema["paths"]["/flows/get_flows_filtered"]["get"]["parameters"][2]["description"] = "End date in format YYYY-MM-DD"
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(here.router, prefix="/here", tags=["here"])
app.include_router(testmongo.router, prefix="/testmongo", tags=["testmongo"])
app.include_router(events.router, prefix="/events", tags=["events"])
app.include_router(flow.router, prefix="/flows", tags=["flows"])
